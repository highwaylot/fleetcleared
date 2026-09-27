# Private: list and act on consultant applications. Requires ?key=<ADMIN_SECRET>, the same env var
# used by api/admin_waitlist.py (set in Vercel: Settings -> Environment Variables). Never put that
# secret in the repo.
#   GET  ?key=...&status=pending|approved|rejected|second_look   -> list applications in that status
#   POST ?key=...  body {id, action: "approve"|"reject"|"second_look"}
# Approving copies a trimmed record into consultants:listings (drops screening internals and IP),
# which is what api/consultants_public.py serves. Also best-effort emails the applicant their
# result via api/_email.py; a failed send never blocks the approve/reject action itself.
import json, os, time, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler

from _email import send_email

SITE = "https://fleetcleared.com"

STATUSES = {"pending", "approved", "rejected", "second_look"}


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


def _all_applications():
    raw = _kv("HGETALL", "consultants:applications").get("result", [])
    return {raw[i]: json.loads(raw[i + 1]) for i in range(0, len(raw), 2)}


class handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _authed(self, qs):
        secret = os.environ.get("ADMIN_SECRET")
        given = (qs.get("key") or [""])[0]
        return bool(secret) and given == secret

    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if not self._authed(qs):
            return self._send(403, {"ok": False, "error": "Wrong or missing key"})
        status = (qs.get("status") or ["pending"])[0]
        if status not in STATUSES:
            return self._send(400, {"ok": False, "error": "Bad status"})
        try:
            apps = _all_applications()
        except Exception as e:
            return self._send(500, {"ok": False, "error": str(e)})
        rows = [a for a in apps.values() if a.get("status") == status]
        self._send(200, {"ok": True, "rows": rows})

    def do_POST(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if not self._authed(qs):
            return self._send(403, {"ok": False, "error": "Wrong or missing key"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._send(400, {"ok": False, "error": "Bad request"})

        app_id = str(data.get("id", "")).strip()
        action = str(data.get("action", "")).strip()
        if action not in ("approve", "reject", "second_look"):
            return self._send(400, {"ok": False, "error": "action must be approve, reject or second_look"})

        try:
            raw = _kv("HGET", "consultants:applications", app_id).get("result")
        except Exception as e:
            return self._send(500, {"ok": False, "error": str(e)})
        if not raw:
            return self._send(404, {"ok": False, "error": "No application with that id"})
        record = json.loads(raw)

        new_status = {"approve": "approved", "reject": "rejected", "second_look": "second_look"}[action]
        record["status"] = new_status
        record["decidedAt"] = int(time.time())
        try:
            _kv("HSET", "consultants:applications", app_id, json.dumps(record))
            if action == "approve":
                listing = {k: v for k, v in record.items() if k not in ("screenScore", "screenBand", "screenBandLabel", "screenReasons", "ip")}
                listing["approvedAt"] = record["decidedAt"]
                _kv("HSET", "consultants:listings", app_id, json.dumps(listing))
            elif new_status != "approved":
                _kv("HDEL", "consultants:listings", app_id)  # in case a previously approved one gets reverted
        except Exception as e:
            return self._send(500, {"ok": False, "error": str(e)})

        if action == "approve":
            send_email(record.get("email"), "Your FleetCleared listing is live",
                       f"{record.get('name', 'Your listing')} is now live on FleetCleared.\n\n"
                       f"Your first lead is free. After that, we need a card on file to deliver paid leads "
                       f"automatically -- add one here:\n{SITE}/add-card.html#{app_id}\n\n"
                       f"No rush: we'll hold your first paid lead for 48 hours if you haven't added one yet.")
        elif action == "reject":
            send_email(record.get("email"), "Your FleetCleared application",
                       f"We couldn't approve {record.get('name', 'your application')} for a FleetCleared listing at this time.\n\n"
                       f"If you think this is a mistake, reply to this email or visit "
                       f"{SITE}/application-status.html and ask for a second look.")

        self._send(200, {"ok": True})
