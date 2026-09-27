# Scheduled job (see vercel.json "crons"): expires leads that have sat on "hold" past the 48-hour
# window terms.html promises ("we hold a new request for up to 48 hours ... If you don't [add a
# card], we tell the carrier you're unavailable"). Nothing else ever revisits a hold, so without
# this a carrier whose consultant never adds a card just waits forever with no answer.
#
# Vercel signs its own cron requests with "Authorization: Bearer $CRON_SECRET" when that env var is
# set (same idea as ADMIN_SECRET elsewhere in api/) -- set CRON_SECRET in Vercel once this is live.
import json, os, time, urllib.request
from http.server import BaseHTTPRequestHandler

from _email import send_email


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

    def do_GET(self):
        secret = os.environ.get("CRON_SECRET")
        if secret and self.headers.get("Authorization") != f"Bearer {secret}":
            return self._send(403, {"ok": False, "error": "forbidden"})

        try:
            raw = _kv("HGETALL", "leads:all").get("result", [])
        except Exception as e:
            return self._send(500, {"ok": False, "error": str(e)})

        now = int(time.time())
        expired = 0
        for i in range(0, len(raw), 2):
            lead_id, lead = raw[i], json.loads(raw[i + 1])
            if lead.get("status") != "hold":
                continue
            if lead.get("holdExpiresAt", 0) > now:
                continue
            lead["status"] = "expired"
            try:
                _kv("HSET", "leads:all", lead_id, json.dumps(lead))
            except Exception:
                continue
            expired += 1
            if lead.get("via") == "email" and lead.get("contact"):
                send_email(lead["contact"], "That consultant wasn't able to take your request",
                           "The consultant you tried to reach through FleetCleared wasn't able to take your "
                           "request in time. Nothing was charged. Browse other consultants: "
                           "https://fleetcleared.com/browse.html")

        self._send(200, {"ok": True, "expired": expired})
