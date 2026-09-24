# Private: returns a raw waitlist (carrier or consultant) so it can be reviewed and copied for a mass
# email later. Requires ?key=<ADMIN_SECRET>, an env var you set in Vercel (Settings -> Environment
# Variables). Never put that secret in the repo; it isn't read from tools/launch.json.
import json, os, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler

LISTS = {"carrier": "waitlist:carrier", "consultant": "waitlist:consultant"}

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
    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        secret = os.environ.get("ADMIN_SECRET")
        given = (qs.get("key") or [""])[0]
        if not secret or not given or given != secret:
            self.send_response(403); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "Wrong or missing key"}).encode())
            return
        which = (qs.get("list") or ["carrier"])[0]
        key = LISTS.get(which, LISTS["carrier"])
        try:
            raw = _kv("LRANGE", key, 0, -1).get("result", [])
            rows = [json.loads(r) for r in raw]
        except Exception as e:
            self.send_response(500); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
            return
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "rows": rows}).encode())
