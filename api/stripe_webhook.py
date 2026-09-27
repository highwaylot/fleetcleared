# Stripe webhook receiver. Configure in the Stripe dashboard: Developers -> Webhooks -> Add
# endpoint -> https://fleetcleared.com/api/stripe_webhook, events "setup_intent.succeeded" and
# "payment_intent.payment_failed". Copy the signing secret it gives you into STRIPE_WEBHOOK_SECRET.
#
# setup_intent.succeeded is the source of truth for "this consultant now has a card on file" --
# api/consultant_card_setup.py only starts the setup; this is what actually saves it, matching
# Stripe's own recommended pattern (never trust the client-side confirmation alone).
import json, os, urllib.request
from http.server import BaseHTTPRequestHandler

from _stripe import verify_webhook_signature
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

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(length)
        secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        if not secret:
            return self._send(500, {"ok": False, "error": "webhook_not_configured"})
        try:
            event = verify_webhook_signature(payload, self.headers.get("Stripe-Signature"), secret)
        except ValueError as e:
            return self._send(400, {"ok": False, "error": str(e)})

        obj = event.get("data", {}).get("object", {})
        etype = event.get("type")

        if etype == "setup_intent.succeeded":
            consultant_id = (obj.get("metadata") or {}).get("consultantId")
            payment_method_id = obj.get("payment_method")
            customer_id = obj.get("customer")
            if consultant_id and payment_method_id:
                try:
                    raw = _kv("HGET", "consultants:listings", consultant_id).get("result")
                    if raw:
                        record = json.loads(raw)
                        record["stripeCustomerId"] = customer_id or record.get("stripeCustomerId")
                        record["stripePaymentMethodId"] = payment_method_id
                        import time
                        record["cardAddedAt"] = int(time.time())
                        _kv("HSET", "consultants:listings", consultant_id, json.dumps(record))
                except Exception:
                    pass  # Stripe retries failed webhooks; a transient KV error isn't fatal here.

        elif etype == "payment_intent.payment_failed":
            consultant_id = (obj.get("metadata") or {}).get("consultantId")
            if consultant_id:
                try:
                    raw = _kv("HGET", "consultants:listings", consultant_id).get("result")
                    if raw:
                        record = json.loads(raw)
                        send_email(record.get("email"), "A FleetCleared charge failed",
                                   "A card charge for a delivered lead failed. Check your payment method at "
                                   f"https://fleetcleared.com/add-card.html#{consultant_id}")
                except Exception:
                    pass

        self._send(200, {"ok": True})
