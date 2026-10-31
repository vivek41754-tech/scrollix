import os
import uuid
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.database.models import Product, Merchant
from app.services.embeddings.embedder import embedder
from app.services.vector_search.faiss_index import vector_index

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["AI Search & Visual Similarity"])

class TextSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    top_k: int = 10

@router.post("/text")
def search_products_by_text(req: TextSearchRequest, db: Session = Depends(get_db)):
    if not req.query.strip():
        return []

    # 1. FAISS Vector Search
    query_vec = embedder.embed_text(req.query)
    similar_hits = vector_index.search_similar(query_vec, top_k=req.top_k * 2, min_score=0.2)
    score_map = {hit["product_id"]: hit["score"] for hit in similar_hits}

    # 2. Query products from DB
    query = db.query(Product).filter(Product.is_active == True)
    if req.category:
        query = query.filter(Product.category.ilike(f"%{req.category}%"))
    if req.min_price is not None:
        query = query.filter(Product.price >= req.min_price)
    if req.max_price is not None:
        query = query.filter(Product.price <= req.max_price)

    products = query.all()

    # 3. Rank products
    scored_results = []
    q_lower = req.query.lower()
    q_words = [w for w in q_lower.split() if len(w) > 2]

    for p in products:
        vector_score = score_map.get(p.id, 0.0)
        # Keyword lexical boost
        lexical_match = 0.0
        p_title_lower = p.title.lower()
        p_desc_lower = p.description.lower()
        p_tags_lower = [t.lower() for t in p.get_tags()]

        if q_lower in p_title_lower:
            lexical_match += 0.5
        elif any(w in p_title_lower for w in q_words):
            lexical_match += 0.35

        if q_lower in p_desc_lower:
            lexical_match += 0.25
        elif any(w in p_desc_lower for w in q_words):
            lexical_match += 0.15

        if any(q_lower in tag for tag in p_tags_lower):
            lexical_match += 0.4
        elif any(w in ' '.join(p_tags_lower) for w in q_words):
            lexical_match += 0.25

        combined_score = round(max(vector_score, lexical_match), 4)
        if combined_score > 0.15:
            scored_results.append({
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "category": p.category,
                "price": p.price,
                "inventory": p.inventory,
                "image_url": p.image_url,
                "tags": p.get_tags(),
                "merchant_id": p.merchant_id,
                "merchant_name": p.merchant.business_name if p.merchant else "Merchant",
                "merchant_city": p.merchant.city if p.merchant else "Local",
                "similarity_score": combined_score
            })

    scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_results[:req.top_k]

@router.post("/visual")
async def search_products_by_image(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    min_price: Optional[float] = Form(None),
    max_price: Optional[float] = Form(None),
    top_k: int = Form(10),
    db: Session = Depends(get_db)
):
    """
    Finds visually similar products using real CLIP image embeddings and FAISS vector index.
    """
    temp_filename = f"temp_search_{uuid.uuid4().hex[:8]}_{file.filename}"
    temp_path = settings.UPLOADS_DIR / temp_filename

    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        # Generate visual embedding and color histogram
        image_vec = embedder.embed_image(str(temp_path))
        image_col = embedder.get_color_histogram(str(temp_path))

        # Search FAISS index using visual features and color reranking
        similar_hits = vector_index.search_similar_visual(image_vec, query_color=image_col, top_k=top_k * 2, min_score=0.1)
        score_map = {hit["product_id"]: hit["score"] for hit in similar_hits}

        if not score_map:
            # Fallback to active products if query score is low
            fallback = db.query(Product).filter(Product.is_active == True).limit(top_k).all()
            return [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "category": p.category,
                    "price": p.price,
                    "inventory": p.inventory,
                    "image_url": p.image_url,
                    "tags": p.get_tags(),
                    "merchant_id": p.merchant_id,
                    "merchant_name": p.merchant.business_name if p.merchant else "Merchant",
                    "merchant_city": p.merchant.city if p.merchant else "Local",
                    "similarity_score": 0.5
                }
                for p in fallback
            ]

        products = db.query(Product).filter(
            Product.id.in_(list(score_map.keys())),
            Product.is_active == True
        ).all()

        results = []
        for p in products:
            if category and category.lower() not in p.category.lower():
                continue
            if min_price is not None and p.price < min_price:
                continue
            if max_price is not None and p.price > max_price:
                continue

            sim_score = score_map.get(p.id, 0.5)
            results.append({
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "category": p.category,
                "price": p.price,
                "inventory": p.inventory,
                "image_url": p.image_url,
                "tags": p.get_tags(),
                "merchant_id": p.merchant_id,
                "merchant_name": p.merchant.business_name if p.merchant else "Merchant",
                "merchant_city": p.merchant.city if p.merchant else "Local",
                "similarity_score": round(sim_score, 4)
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    finally:
        if temp_path.exists():
            temp_path.unlink()

@router.post("/rebuild-index")
def rebuild_faiss_index(db: Session = Depends(get_db)):
    """Reindexes all active products into FAISS vector database."""
    count = vector_index.sync_catalogue_visual_index(db, embedder)
    return {"message": f"Successfully indexed {count} products in FAISS.", "index_total": vector_index.index.ntotal}
