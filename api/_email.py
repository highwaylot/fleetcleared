# Transactional email via Resend's REST API (https://resend.com). One urllib call, no SDK --
# matches the rest of api/'s zero-dependency style. Requires RESEND_API_KEY and RESEND_FROM
# (a verified sender, e.g. "FleetCleared <hello@fleetcleared.com>") in Vercel's env vars.
# Leading underscore: not its own route, importable by other api/*.py files.
import json, os, urllib.request


def send_email(to, subject, text):
    """Best-effort send. Returns True on success, False on any failure (never raises) so a
    notification going out never blocks the caller's main job (saving a lead, approving a listing)."""
    api_key = os.environ.get("RESEND_API_KEY")
    sender = os.environ.get("RESEND_FROM")
    if not api_key or not sender:
        return False
    body = json.dumps({"from": sender, "to": [to], "subject": subject, "text": text}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=body, headers={
        "Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return 200 <= r.status < 300
    except Exception:
        return False
