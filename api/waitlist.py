# Stores directory-waitlist signups in Vercel KV (Upstash Redis), called from the home page form.
# No email is sent from here. See api/admin_waitlist.py to read the list back.
import json, os, re, time, urllib.request

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_LEN = 200

def _kv_url():
    return os.environ.get("KV_REST_API_URL") or os.environ.get("UPSTASH_REDIS_REST_URL")

def _kv_token():
    return os.environ.get("KV_REST_API_TOKEN") or os.environ.get("UPSTASH_REDIS_REST_TOKEN")

def _kv(*command):
    url, token = _kv_url(), _kv_token()
    if not url or not token:
        raise RuntimeError("Vercel KV isn't connected yet (KV_REST_API_URL / KV_REST_API_TOKEN missing)")
    req = urllib.request.Request(url, data=json.dumps(list(command)).encode(), headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read())

def _clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()[:MAX_LEN]

from http.server import BaseHTTPRequestHandler

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
            return self._send(400, {"ok": False, "error": "Bad request"})

        if _clean(data.get("botcheck")):  # honeypot: real visitors never fill this hidden field
            return self._send(200, {"ok": True})  # pretend success, drop it silently

        email = _clean(data.get("email")).lower()
        if not EMAIL_RE.match(email):
            return self._send(400, {"ok": False, "error": "Enter a full email address."})

        record = {"email": email, "name": _clean(data.get("name")), "state": _clean(data.get("state")).upper()[:2], "ts": int(time.time())}
        try:
            _kv("RPUSH", "waitlist", json.dumps(record))
        except Exception as e:
            return self._send(500, {"ok": False, "error": "Couldn't save that right now. Try again in a bit."})
        self._send(200, {"ok": True})
