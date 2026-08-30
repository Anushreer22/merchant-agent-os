import json
import hmac
import hashlib
import urllib.request

secret = "whsec_demo123"
order_id = "order_TVqLoSjmkVelRQ"

payload = {
    "id": "evt_test_manual",
    "event": "payment.captured",
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_test_manual",
                "order_id": order_id,
                "status": "captured",
                "amount": 850000,
                "currency": "INR"
            }
        }
    }
}

# Canonicalize as backend likely does: sorted keys, compact separators
body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
signature = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/webhooks/razorpay",
    data=body.encode(),
    headers={
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature,
    },
)

try:
    with urllib.request.urlopen(req) as resp:
        print("Status:", resp.status)
        print("Response:", resp.read().decode())
except urllib.error.HTTPError as e:
    print("Status:", e.code)
    print("Response:", e.read().decode())
