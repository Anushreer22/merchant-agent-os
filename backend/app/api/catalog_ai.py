from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.services.auth_service import get_current_user
from app.config import settings

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    buyer_id: Optional[str] = None


class DescriptionRequest(BaseModel):
    name: str
    keywords: list[str] = []
    tone: str = "professional"


def _llm_search(query: str, products: list) -> list[dict]:
    """Use OpenAI to extract intent and score products."""
    if not settings.OPENAI_API_KEY:
        # Fallback: simple keyword match
        q = query.lower()
        results = []
        for p in products:
            score = 0
            if p.category and p.category.lower() in q:
                score += 2
            if p.name and any(w in q for w in p.name.lower().split()):
                score += 1
            if p.description and any(w in q for w in q.split() if len(w) > 3 and w in (p.description or "").lower()):
                score += 1
            results.append({"product": p, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:3]

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        catalog_summary = "\n".join(
            f"- {p.product_id}: {p.name} ({p.category}), ₹{p.base_price}" for p in products
        )
        resp = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a product search assistant. Given a user query and product catalog, return the top 3 most relevant product_ids as a JSON array. Only return the JSON array, nothing else."},
                {"role": "user", "content": f"Query: {query}\n\nCatalog:\n{catalog_summary}"},
            ],
            max_tokens=100,
            temperature=0,
        )
        import json
        ids = json.loads(resp.choices[0].message.content.strip())
        product_map = {p.product_id: p for p in products}
        return [{"product": product_map[pid], "score": 3 - i}
                for i, pid in enumerate(ids) if pid in product_map]
    except Exception:
        # Fallback on any error
        return [{"product": p, "score": 1} for p in products[:3]]


@router.post("/search")
def search_catalog(
    body: SearchRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    products = db.query(Product).filter(Product.availability == True).all()
    if not products:
        return {"results": []}

    matches = _llm_search(body.query, products)
    return {
        "query": body.query,
        "results": [
            {
                "product_id": m["product"].product_id,
                "name": m["product"].name,
                "category": m["product"].category,
                "base_price": float(m["product"].base_price),
                "currency": m["product"].currency,
                "description": m["product"].description,
                "score": m["score"],
            }
            for m in matches
        ],
    }


@router.post("/generate-description")
def generate_description(
    body: DescriptionRequest,
    _: User = Depends(get_current_user),
):
    if not settings.OPENAI_API_KEY:
        # Fallback: template-based description
        kw = ", ".join(body.keywords) if body.keywords else "premium features"
        return {"description": f"{body.name} — a {body.tone} solution featuring {kw}. Designed for modern businesses seeking efficiency and reliability."}

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        kw_str = ", ".join(body.keywords) if body.keywords else "general use"
        resp = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": f"Write a {body.tone} product description in 2-3 sentences."},
                {"role": "user", "content": f"Product: {body.name}\nKeywords: {kw_str}"},
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return {"description": resp.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {str(e)}")
