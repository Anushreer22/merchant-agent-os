from fastapi import APIRouter, Query, HTTPException
from app.config import EXCHANGE_RATES

router = APIRouter()


@router.get("/convert")
def convert_currency(
    from_currency: str = Query(..., alias="from"),
    to_currency: str = Query(..., alias="to"),
    amount: float = Query(..., gt=0),
):
    from_c = from_currency.upper()
    to_c = to_currency.upper()
    if from_c not in EXCHANGE_RATES:
        raise HTTPException(status_code=400, detail=f"Unsupported currency: {from_c}")
    if to_c not in EXCHANGE_RATES:
        raise HTTPException(status_code=400, detail=f"Unsupported currency: {to_c}")

    # Convert via INR as base
    amount_inr = amount / EXCHANGE_RATES[from_c]
    converted = round(amount_inr * EXCHANGE_RATES[to_c], 4)
    return {
        "from": from_c, "to": to_c,
        "original_amount": amount,
        "converted_amount": converted,
        "rate": round(EXCHANGE_RATES[to_c] / EXCHANGE_RATES[from_c], 6),
    }


def convert_amount(amount: float, from_currency: str, to_currency: str) -> float:
    """Helper for internal use."""
    f = from_currency.upper()
    t = to_currency.upper()
    if f not in EXCHANGE_RATES or t not in EXCHANGE_RATES:
        return amount
    return round((amount / EXCHANGE_RATES[f]) * EXCHANGE_RATES[t], 2)
