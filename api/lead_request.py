# The actual lead-delivery endpoint. Public POST, no auth (a carrier submitting the "Request
# contact" form). Runs the pricing/decision spec in _rules.py, attempts a Stripe off-session charge
# when one is owed, emails the consultant the lead when it's actually delivered, and never hands
# raw contact details to a consultant who hasn't paid or isn't going to (hold/decline).
#
# This replaces what the site used to do: assets/site.js's contact-form submit handler only wrote
# to localStorage and showed a fake "Request sent" message. It never reached any backend, so no
# lead was ever billed or delivered. See README.md for the env vars this needs (Stripe, Resend).
import json, os, re, time, urllib.request
from http.server import BaseHTTPRequestHandler

from _rules import decide_lead
from _email import send_email
from _stripe import create_off_session_charge, StripeError

MAX_LEN = 2000
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
HOLD_HOURS = 48
SITE = "https://fleetcleared.com"


def _kv_url():
    return os.environ.get("KV_REST_API_URL") or os.environ.get("UPSTASH_REDIS_REST_URL")

def _kv_token():
    return os.environ.get("KV_REST_API_TOKEN") or os.environ.get("UPSTASH_REDIS_REST_TOKEN")

def _kv(*command):
    url, token = _kv_url(), _kv_token()
    if not url or not token:
        raise RuntimeError("Vercel KV isn't connected yet")
    req = urllib.request.Request(url, data=json.dumps(list(command)).encode(), headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read())


def _clean(s, max_len=MAX_LEN):
    return re.sub(r"\s+", " ", str(s or "")).strip()[:max_len]

def _digits(s):
    return re.sub(r"\D", "", str(s or ""))

def _month_key(t=None):
    return time.strftime("%Y-%m", time.gmtime(t))


def _account_for(record):
    stored_month = record.get("leadsMonthKey")
    leads_this_month = record.get("leadsThisMonth", 0) if stored_month == _month_key() else 0
    cap_raw = record.get("monthlyCap")
    monthly_cap = int(cap_raw) if str(cap_raw or "").isdigit() else None
    return {
        "freeLeadUsedByBusiness": bool(record.get("freeLeadUsed")),
        "cardOnFile": bool(record.get("stripePaymentMethodId")),
        "leadsThisMonth": leads_this_month,
        "monthlyCap": monthly_cap,
    }, leads_this_month


def _mark_delivered(record, leads_this_month):
    record["freeLeadUsed"] = True
    record["leadsThisMonth"] = leads_this_month + 1
    record["leadsMonthKey"] = _month_key()


class handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._send(400, {"ok": False, "error": "bad_request"})

        if _clean(data.get("botcheck")):
            return self._send(200, {"ok": True})  # honeypot: pretend success, drop it

        consultant_id = _clean(data.get("consultantId"), 40)
        carrier_name = _clean(data.get("name"), 200)
        company = _clean(data.get("company"), 200)
        via = _clean(data.get("via"), 10) or "call"
        contact = _clean(data.get("contact"), 200)
        need = _clean(data.get("need"), 500)
        try:
            fleet_size = int(data.get("fleet"))
        except (TypeError, ValueError):
            fleet_size = None

        if not consultant_id or not carrier_name or not fleet_size or fleet_size < 1:
            return self._send(400, {"ok": False, "error": "bad_request"})
        if via == "email":
            if not EMAIL_RE.match(contact):
                return self._send(400, {"ok": False, "error": "bad_contact"})
        else:
            if len(_digits(contact)) < 10:
                return self._send(400, {"ok": False, "error": "bad_contact"})

        try:
            raw = _kv("HGET", "consultants:listings", consultant_id).get("result")
        except Exception:
            return self._send(500, {"ok": False, "error": "store_unreachable"})
        if not raw:
            return self._send(404, {"ok": False, "error": "not_found"})
        record = json.loads(raw)

        account, leads_this_month = _account_for(record)
        decision = decide_lead(account, fleet_size)

        lead_id = os.urandom(8).hex()
        lead = {
            "id": lead_id, "consultantId": consultant_id, "carrierName": carrier_name,
            "company": company, "fleetSize": fleet_size, "via": via, "contact": contact,
            "need": need, "createdAt": int(time.time()), "action": decision["action"],
            "charge": decision["charge"], "status": decision["action"],
        }

        if decision["action"] == "decline":
            try:
                _kv("HSET", "leads:all", lead_id, json.dumps(lead))
            except Exception:
                pass
            return self._send(200, {"ok": False, "error": "not_accepting"})

        if decision["action"] == "deliver" and decision["charge"] > 0:
            try:
                pi = create_off_session_charge(
                    record["stripeCustomerId"], record["stripePaymentMethodId"],
                    decision["charge"] * 100, "usd",
                    f"FleetCleared lead: {company or carrier_name}", idempotency_key=lead_id,
                    metadata={"consultantId": consultant_id, "leadId": lead_id})
                lead["stripePaymentIntentId"] = pi.get("id")
            except (StripeError, KeyError, RuntimeError) as e:
                # Card missing or declined: treat like "no card on file" -- hold and ask the
                # consultant to fix their payment method, same 48h window as a true hold.
                lead["status"] = "hold"
                lead["holdReason"] = "charge_failed"
                lead["holdExpiresAt"] = int(time.time()) + HOLD_HOURS * 3600
                try:
                    _kv("HSET", "leads:all", lead_id, json.dumps(lead))
                except Exception:
                    pass
                send_email(record.get("email"), "Your card was declined for a new FleetCleared lead",
                           f"A carrier tried to reach you through FleetCleared, but your card on file was declined.\n\n"
                           f"Update your payment method within {HOLD_HOURS} hours to receive this lead:\n"
                           f"{SITE}/add-card.html#{consultant_id}\n\n"
                           f"If you don't, we'll tell the carrier you're unavailable and they'll be free to contact someone else.")
                return self._send(200, {"ok": True})

        if decision["action"] == "hold":
            lead["holdExpiresAt"] = int(time.time()) + HOLD_HOURS * 3600
            try:
                _kv("HSET", "leads:all", lead_id, json.dumps(lead))
            except Exception:
                pass
            send_email(record.get("email"), "You have a new FleetCleared lead waiting",
                       f"A carrier tried to reach you through FleetCleared. Your free lead has already been used, "
                       f"so we need a payment method on file before we hand over their details.\n\n"
                       f"Add one within {HOLD_HOURS} hours to receive this lead:\n"
                       f"{SITE}/add-card.html#{consultant_id}\n\n"
                       f"If you don't, we'll tell the carrier you're unavailable and they'll be free to contact someone else.")
            return self._send(200, {"ok": True})

        # action == 'deliver' (free lead, or a card charge that just succeeded above)
        _mark_delivered(record, leads_this_month)
        try:
            _kv("HSET", "consultants:listings", consultant_id, json.dumps(record))
            _kv("HSET", "leads:all", lead_id, json.dumps(lead))
        except Exception:
            return self._send(500, {"ok": False, "error": "store_unreachable"})

        contact_line = f"Email: {contact}" if via == "email" else f"Phone: {contact}"
        charge_line = (f"You were charged ${decision['charge']} for this lead."
                       if decision["charge"] > 0 else "This was your one free lead -- no charge.")
        send_email(record.get("email"), f"New FleetCleared lead: {carrier_name}",
                   f"{carrier_name} ({company or 'no company given'}) wants to hear from you.\n\n"
                   f"Fleet size: {fleet_size} truck{'s' if fleet_size != 1 else ''}\n"
                   f"Prefers: {via}\n{contact_line}\n"
                   + (f"What they need help with: {need}\n" if need else "")
                   + f"\n{charge_line}")

        self._send(200, {"ok": True})
