# Direct calls to Stripe's REST API via urllib -- no stripe-python dependency, matching the rest
# of api/'s zero-dependency style (this project has no requirements.txt at all). Stripe's API is
# plain form-encoded POST + bearer auth, so this is a thin wrapper, not a reimplementation of the SDK.
# Leading underscore: not its own route, importable by other api/*.py files.
import hashlib, hmac, json, os, urllib.error, urllib.parse, urllib.request

API_BASE = "https://api.stripe.com/v1"


def _secret_key():
    return os.environ.get("STRIPE_SECRET_KEY")


def _request(method, path, data=None):
    key = _secret_key()
    if not key:
        raise RuntimeError("Stripe isn't connected yet (STRIPE_SECRET_KEY is not set)")
    body = urllib.parse.urlencode(data or {}, doseq=True).encode() if data is not None else None
    req = urllib.request.Request(f"{API_BASE}/{path}", data=body, method=method,
                                  headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read())
        except Exception:
            err = {"error": {"message": str(e)}}
        raise StripeError(err.get("error", {}).get("message", "Stripe request failed"), err) from None


class StripeError(Exception):
    def __init__(self, message, payload=None):
        super().__init__(message)
        self.payload = payload or {}


def create_customer(email, name, metadata=None):
    data = {"email": email, "name": name}
    for k, v in (metadata or {}).items():
        data[f"metadata[{k}]"] = v
    return _request("POST", "customers", data)


def create_setup_intent(customer_id, metadata=None):
    data = {
        "customer": customer_id,
        "usage": "off_session",
        "payment_method_types[]": "card",
    }
    for k, v in (metadata or {}).items():
        data[f"metadata[{k}]"] = v
    return _request("POST", "setup_intents", data)


def retrieve_setup_intent(setup_intent_id):
    return _request("GET", f"setup_intents/{setup_intent_id}")


def create_off_session_charge(customer_id, payment_method_id, amount_cents, currency, description, idempotency_key=None, metadata=None):
    """Charges a previously-saved card with no customer present. Raises StripeError on decline/failure
    -- the caller decides what that means for lead delivery (hold, notify, etc.), same as any other
    payment failure; this helper only talks to Stripe."""
    data = {
        "amount": amount_cents,
        "currency": currency,
        "customer": customer_id,
        "payment_method": payment_method_id,
        "off_session": "true",
        "confirm": "true",
        "description": description,
    }
    for k, v in (metadata or {}).items():
        data[f"metadata[{k}]"] = v
    key = _secret_key()
    if not key:
        raise RuntimeError("Stripe isn't connected yet (STRIPE_SECRET_KEY is not set)")
    body = urllib.parse.urlencode(data, doseq=True).encode()
    headers = {"Authorization": f"Bearer {key}"}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    req = urllib.request.Request(f"{API_BASE}/payment_intents", data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read())
        except Exception:
            err = {"error": {"message": str(e)}}
        raise StripeError(err.get("error", {}).get("message", "Card charge failed"), err) from None


def verify_webhook_signature(payload_bytes, sig_header, secret, tolerance_seconds=300):
    """Implements Stripe's documented signing scheme (HMAC-SHA256 over "{timestamp}.{payload}")
    without the SDK. Returns the parsed event dict, or raises ValueError if the signature or
    timestamp doesn't check out."""
    if not sig_header:
        raise ValueError("Missing Stripe-Signature header")
    parts = dict(p.split("=", 1) for p in sig_header.split(",") if "=" in p)
    timestamp, v1 = parts.get("t"), parts.get("v1")
    if not timestamp or not v1:
        raise ValueError("Malformed Stripe-Signature header")
    signed_payload = f"{timestamp}.".encode() + payload_bytes
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, v1):
        raise ValueError("Signature mismatch")
    import time
    if abs(time.time() - int(timestamp)) > tolerance_seconds:
        raise ValueError("Timestamp outside tolerance")
    return json.loads(payload_bytes)
