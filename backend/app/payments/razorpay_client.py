import razorpay
from app.config import settings

_client = None


def get_razorpay_client() -> razorpay.Client:
    global _client
    if _client is None:
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            raise RuntimeError(
                "Razorpay credentials are not configured. "
                "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in your environment."
            )
        _client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    return _client
