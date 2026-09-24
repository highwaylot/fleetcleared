# Consultant application intake. Public POST endpoint, no auth (matches the site's "submit for
# review" copy). Screens the applicant against every other application already on file, using the
# same signals as assets/rules.js SCREENING -- that file is the spec; keep both in sync by hand.
# Only signals we can actually compute from a submitted form are included: no external lookups
# exist yet (state registry, phone-line type, domain age, web presence, association membership),
# so those signals are left out entirely rather than faked, matching "a lookup that hasn't run
# adds no points."
# Stores the application in Vercel KV (Upstash Redis) as status "pending". See
# api/admin_consultants.py for the review/approve flow, and README.md for the storage setup steps.
import json, os, re, time, urllib.request
from http.server import BaseHTTPRequestHandler

MAX_LEN = 2000
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
FREE_EMAIL_DOMAINS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
                       "icloud.com", "live.com", "msn.com", "proton.me", "protonmail.com"}
GOV_WORDS = re.compile(r"\b(department of transportation|fmcsa|federal motor carrier|usdot|u\.s\. dot|government|official|dot authority)\b", re.I)
GOV_CLAIMS = re.compile(
    r"\b(official (fmcsa|usdot|dot|government|federal)|(a|an|the) (government|federal|state) agency|"
    r"on behalf of (the )?(fmcsa|usdot|dot|department of transportation|government)|"
    r"(affiliated|partnered) with (the )?(fmcsa|usdot|dot|department of transportation)|"
    r"government[- ](approved|authorized|official)|(fmcsa|dot|usdot)[- ](approved|authorized|certified|official))\b", re.I)
NAME_NOISE = {"llc", "inc", "co", "corp", "company", "the", "group", "services", "service"}
BANDS = [(24, "clear", "Clear"), (59, "check", "Check"), (float("inf"), "hold", "Hold")]


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


def _norm_phone(s):
    return _digits(s)[-10:]


def _norm_name(n):
    words = re.sub(r"[^a-z0-9 ]", " ", str(n or "").lower()).split()
    return " ".join(w for w in words if w and w not in NAME_NOISE)


def _similarity(a, b):
    """Dice coefficient on letter pairs, matching rules.js's similarity() exactly."""
    a, b = _norm_name(a).replace(" ", ""), _norm_name(b).replace(" ", "")
    if not a or not b:
        return 0
    if a == b:
        return 1
    def pairs(s):
        m = {}
        for i in range(len(s) - 1):
            p = s[i:i + 2]
            m[p] = m.get(p, 0) + 1
        return m
    pa, pb = pairs(a), pairs(b)
    overlap = sum(min(n, pb.get(p, 0)) for p, n in pa.items())
    return (2 * overlap) / (len(a) - 1 + len(b) - 1)


def _screen(applicant, existing):
    hits = []
    phone = _norm_phone(applicant.get("phone"))
    if phone:
        m = next((e for e in existing if _norm_phone(e.get("phone")) == phone), None)
        if m: hits.append({"key": "samePhone", "points": 60, "reason": f"Same phone number as {m.get('name', 'another applicant')}"})

    ip = applicant.get("ip")
    if ip:
        m = next((e for e in existing if e.get("ip") == ip), None)
        if m: hits.append({"key": "sameRecentIp", "points": 25, "reason": f"Applied from the same internet address as {m.get('name', 'another applicant')} recently"})

    m = next((e for e in existing if _similarity(e.get("name"), applicant.get("name")) >= 0.9), None)
    if m: hits.append({"key": "similarName", "points": 25, "reason": f"Company name nearly matches {m.get('name', 'another applicant')}"})

    domain = str(applicant.get("email", "")).lower().split("@")[-1] if "@" in str(applicant.get("email", "")) else ""
    if domain in FREE_EMAIL_DOMAINS:
        hits.append({"key": "freeEmail", "points": 10, "reason": "Uses a free email address"})

    if GOV_WORDS.search(applicant.get("name") or "") or GOV_CLAIMS.search(applicant.get("description") or ""):
        hits.append({"key": "governmentStyle", "points": 25, "reason": "Name or description may suggest a government agency"})

    score = max(0, sum(h["points"] for h in hits))
    band_key, band_label = next((k, l) for max_, k, l in BANDS if score <= max_)
    return {"score": score, "band": band_key, "bandLabel": band_label, "reasons": hits}


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

        if _clean(data.get("botcheck")):
            return self._send(200, {"ok": True, "id": "ok"})  # honeypot: pretend success, drop it

        name = _clean(data.get("name"), 200)
        email = _clean(data.get("email"), 200).lower()
        phone = _clean(data.get("phone"), 40)
        states = _clean(data.get("states"), 200)
        if not name or not EMAIL_RE.match(email) or not phone or not states:
            return self._send(400, {"ok": False, "error": "Company name, work email, phone and states served are required."})
        if not data.get("agree"):
            return self._send(400, {"ok": False, "error": "You need to agree to the terms and privacy policy to apply."})
        if _clean(data.get("cap", ""), 10) not in ("5", "10", "20", ""):
            return self._send(400, {"ok": False, "error": "Bad request"})

        applicant = {
            "name": name, "email": email, "phone": phone, "states": states,
            "contactPref": _clean(data.get("contactPref"), 10) or "call",
            "timezone": _clean(data.get("timezone"), 20) or "Central",
            "monthlyCap": _clean(data.get("cap"), 10),
            "hours": _clean(data.get("hours"), 200),
            "specialties": _clean(data.get("specialties"), 300),
            "description": _clean(data.get("description"), 300),
            "ip": self.headers.get("x-forwarded-for", "").split(",")[0].strip() or None,
        }

        try:
            existing_raw = _kv("HGETALL", "consultants:applications").get("result", [])
            existing = [json.loads(existing_raw[i + 1]) for i in range(0, len(existing_raw), 2)]
        except Exception:
            return self._send(500, {"ok": False, "error": "Couldn't reach the application store right now. Try again in a bit."})

        result = _screen(applicant, existing)
        app_id = os.urandom(8).hex()
        record = {**applicant, "id": app_id, "status": "pending", "submittedAt": int(time.time()),
                   "screenScore": result["score"], "screenBand": result["band"], "screenBandLabel": result["bandLabel"],
                   "screenReasons": result["reasons"]}
        try:
            _kv("HSET", "consultants:applications", app_id, json.dumps(record))
        except Exception:
            return self._send(500, {"ok": False, "error": "Couldn't save your application right now. Try again in a bit."})

        self._send(200, {"ok": True, "id": app_id})
