# Public, no auth: every approved consultant listing, trimmed to only what the directory UI shows.
# IMPORTANT: never add email/phone/stripe*/ip/leadsThisMonth back into PUBLIC_FIELDS below. Contact
# only ever reaches a consultant through /api/lead_request, which is how leads get billed; leaking
# raw contact details here would let anyone skip that entirely and defeats the whole pay-per-lead
# model. assets/site.js's mapListing() is the contract for what the frontend actually reads.
import json, os, urllib.request
from http.server import BaseHTTPRequestHandler

PUBLIC_FIELDS = ("id", "name", "states", "specialties", "description", "contactPref", "timezone", "hours", "approvedAt")

# Fake listings so Preview deploys look populated for demos/testing. Vercel sets VERCEL_ENV to
# "production" only on the real site -- these never show there. Ids are prefixed "demo-" so they're
# obviously not real KV records if anyone goes looking.
DEMO_LISTINGS = [
    {"id": "demo-1", "name": "Lone Star Compliance Group", "states": "TX",
     "specialties": "DOT/MC setup, BOC-3, UCR, DQ files", "contactPref": "call", "timezone": "Central",
     "hours": "Mon-Fri 8am-5pm", "description": "Texas-based, small-fleet focused. 8 years in trucking compliance.",
     "approvedAt": 1759190400, "atLimit": False},
    {"id": "demo-2", "name": "Gulf Coast Safety Consultants", "states": "TX",
     "specialties": "Audit readiness, HOS/ELD, drug & alcohol program setup", "contactPref": "email",
     "timezone": "Central", "hours": "Mon-Sat 7am-6pm", "description": "Houston area, 12 years in trucking compliance.",
     "approvedAt": 1759190400, "atLimit": False},
    {"id": "demo-3", "name": "Panhandle DOT Advisors", "states": "TX",
     "specialties": "IFTA, UCR, MCS-150 updates", "contactPref": "call", "timezone": "Central",
     "hours": "Mon-Fri 9am-5pm", "description": "Amarillo, serves rural fleets.",
     "approvedAt": 1759190400, "atLimit": False},
    {"id": "demo-4", "name": "Rio Grande Fleet Compliance", "states": "TX",
     "specialties": "New authority setup, BOC-3, DQ files", "contactPref": "text", "timezone": "Central",
     "hours": "Mon-Fri 8am-6pm", "description": "Border-region carriers, bilingual support.",
     "approvedAt": 1759190400, "atLimit": False},
    {"id": "demo-5", "name": "Metroplex Trucking Safety", "states": "TX",
     "specialties": "Mock audits, CSA score monitoring, driver files", "contactPref": "email",
     "timezone": "Central", "hours": "Mon-Fri 8am-5pm", "description": "DFW area, works with fleets up to 20 trucks.",
     "approvedAt": 1759190400, "atLimit": True},
]


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


def _public_row(r):
    row = {k: r.get(k) for k in PUBLIC_FIELDS}
    cap = r.get("monthlyCap")
    cap = int(cap) if str(cap or "").isdigit() else None
    row["atLimit"] = cap is not None and r.get("leadsThisMonth", 0) >= cap
    return row


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            raw = _kv("HGETALL", "consultants:listings").get("result", [])
            rows = [_public_row(json.loads(raw[i + 1])) for i in range(0, len(raw), 2)]
        except Exception as e:
            self.send_response(500); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
            return
        if os.environ.get("VERCEL_ENV") != "production":
            rows = DEMO_LISTINGS + rows
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "public, max-age=60")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "rows": rows}).encode())
