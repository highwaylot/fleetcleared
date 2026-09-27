# Lets an approved consultant add a card, without our server ever touching the card number.
# Public, no separate auth: the consultant id itself is the capability (a 16-hex-char random id,
# same trust model consultant.html and application-status.html already use for their deep links --
# it's only ever emailed to that consultant, never listed anywhere public).
#   GET  ?id=<consultantId>   -> {ok, hasCard}
#   POST {id}                 -> creates/reuses a Stripe Customer + SetupIntent, returns a client
#                                 secret for Stripe.js (assets/stripe-card.js on add-card.html) to
#                                 collect the card directly with Stripe -- the raw card number
#                                 never reaches this server, only Stripe sees it.
# api/stripe_webhook.py is what actually saves the resulting payment method once Stripe confirms it.
import json, os, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler

from _stripe import create_customer, create_setup_intent, StripeError


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


class handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _record(self, consultant_id):
        raw = _kv("HGET", "consultants:listings", consultant_id).get("result")
        return json.loads(raw) if raw else None

    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        consultant_id = (qs.get("id") or [""])[0].strip()
        if not consultant_id:
            return self._send(400, {"ok": False, "error": "bad_request"})
        try:
            record = self._record(consultant_id)
        except Exception:
            return self._send(500, {"ok": False, "error": "store_unreachable"})
        if not record:
            return self._send(404, {"ok": False, "error": "not_found"})
        self._send(200, {"ok": True, "name": record.get("name"), "hasCard": bool(record.get("stripePaymentMethodId"))})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._send(400, {"ok": False, "error": "bad_request"})
        consultant_id = str(data.get("id", "")).strip()
        if not consultant_id:
            return self._send(400, {"ok": False, "error": "bad_request"})

        try:
            record = self._record(consultant_id)
        except Exception:
            return self._send(500, {"ok": False, "error": "store_unreachable"})
        if not record:
            return self._send(404, {"ok": False, "error": "not_found"})

        try:
            customer_id = record.get("stripeCustomerId")
            if not customer_id:
                customer = create_customer(record.get("email"), record.get("name"), metadata={"consultantId": consultant_id})
                customer_id = customer["id"]
                record["stripeCustomerId"] = customer_id
                _kv("HSET", "consultants:listings", consultant_id, json.dumps(record))
            setup_intent = create_setup_intent(customer_id, metadata={"consultantId": consultant_id})
        except StripeError as e:
            return self._send(502, {"ok": False, "error": str(e)})
        except Exception:
            return self._send(500, {"ok": False, "error": "store_unreachable"})

        publishable_key = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
        self._send(200, {"ok": True, "clientSecret": setup_intent["client_secret"], "publishableKey": publishable_key})
