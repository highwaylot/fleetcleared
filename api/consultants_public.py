# Public, no auth: every approved consultant listing. Not wired into browse.html/consultant.html
# yet -- those still read window.FC_DEMO_CONSULTANTS in the preview build and are not part of the
# public launch build at all. This endpoint exists so that wiring is a frontend-only follow-up,
# not another backend build.
import json, os, urllib.request
from http.server import BaseHTTPRequestHandler


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
        try:
            raw = _kv("HGETALL", "consultants:listings").get("result", [])
            rows = [json.loads(raw[i + 1]) for i in range(0, len(raw), 2)]
        except Exception as e:
            self.send_response(500); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "public, max-age=60")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "rows": rows}).encode())
