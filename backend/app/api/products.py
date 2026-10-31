from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Product, Merchant, User, Review, Interaction
from app.api.auth import require_current_user, get_current_user
from app.services.embeddings.embedder import embedder
from app.services.vector_search.faiss_index import vector_index
from app.services.sentiment.analyzer import sentiment_analyzer

router = APIRouter(prefix="/products", tags=["Products"])

class CreateProductRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = "General"
    price: float
    inventory: int = 10
    image_url: Optional[str] = ""
    tags: list[str] = []

class CreateReviewRequest(BaseModel):
    rating: int = 5
    comment: str

class InteractRequest(BaseModel):
    interaction_type: str  # view, like, click, purchase_intent
    dwell_time: float = 0.0

@router.get("")
def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    merchant_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_active == True)
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if merchant_id is not None:
        query = query.filter(Product.merchant_id == merchant_id)
    if search:
        query = query.filter(Product.title.ilike(f"%{search}%") | Product.description.ilike(f"%{search}%"))

    products = query.all()
    return [
        {
            "id": p.id,
            "merchant_id": p.merchant_id,
            "merchant_name": p.merchant.business_name if p.merchant else "Merchant",
            "merchant_city": p.merchant.city if p.merchant else "Local",
            "merchant_verified": p.merchant.is_verified if p.merchant else False,
            "merchant_trust_score": p.merchant.trust_score if p.merchant else 75.0,
            "title": p.title,
            "description": p.description,
            "category": p.category,
            "price": p.price,
            "inventory": p.inventory,
            "image_url": p.image_url,
            "tags": p.get_tags(),
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in products
    ]

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found.")

    # Calculate sentiment summary from reviews
    reviews_data = [
        {
            "id": r.id,
            "username": r.user.username if r.user else "Anonymous",
            "rating": r.rating,
            "comment": r.comment,
            "sentiment_score": r.sentiment_score,
            "sentiment_label": r.sentiment_label,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in p.reviews
    ]
    sentiment_summary = sentiment_analyzer.aggregate_reviews(reviews_data)

    return {
        "id": p.id,
        "merchant_id": p.merchant_id,
        "merchant_name": p.merchant.business_name if p.merchant else "Merchant",
        "merchant_city": p.merchant.city if p.merchant else "Local",
        "merchant_verified": p.merchant.is_verified if p.merchant else False,
        "merchant_trust_score": p.merchant.trust_score if p.merchant else 75.0,
        "title": p.title,
        "description": p.description,
        "category": p.category,
        "price": p.price,
        "inventory": p.inventory,
        "image_url": p.image_url,
        "tags": p.get_tags(),
        "reviews": reviews_data,
        "sentiment_summary": sentiment_summary
    }

@router.post("")
def create_product(req: CreateProductRequest, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    merchant = db.query(Merchant).filter(Merchant.user_id == user.id).first()
    if not merchant:
        raise HTTPException(status_code=400, detail="You must register as a merchant before adding products.")

    product = Product(
        merchant_id=merchant.id,
        title=req.title,
        description=req.description,
        category=req.category,
        price=req.price,
        inventory=req.inventory,
        image_url=req.image_url or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600"
    )
    product.set_tags(req.tags)
    db.add(product)
    db.commit()
    db.refresh(product)

    # Embed and index product in FAISS
    vec = embedder.embed_text(f"{product.title} {product.category} {product.description}")
    vector_index.add_product(product.id, vec)
    product.embedding_id = product.id
    db.commit()

    return {
        "id": product.id,
        "title": product.title,
        "message": "Product created and indexed in FAISS vector database."
    }

@router.delete("/{product_id}")
def delete_product(product_id: int, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    if user.role != "admin" and (not user.merchant or user.merchant.id != product.merchant_id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this product.")

    # Remove from FAISS index
    vector_index.remove_product(product.id)

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully."}

@router.post("/{product_id}/reviews")
def add_product_review(product_id: int, req: CreateReviewRequest, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # Analyze comment sentiment locally
    sentiment = sentiment_analyzer.analyze_text(req.comment)

    review = Review(
        user_id=user.id,
        product_id=product.id,
        rating=max(1, min(5, req.rating)),
        comment=req.comment,
        sentiment_score=sentiment["polarity"],
        sentiment_label=sentiment["label"]
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "id": review.id,
        "sentiment": sentiment,
        "message": "Review submitted and analyzed."
    }

@router.post("/{product_id}/interact")
def record_interaction(
    product_id: int,
    req: InteractRequest,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    user_id = user.id if user else 1  # Fallback to guest / demo user
    it = Interaction(
        user_id=user_id,
        product_id=product_id,
        interaction_type=req.interaction_type,
        dwell_time=req.dwell_time
    )
    db.add(it)
    db.commit()

    return {"status": "success", "recorded_type": req.interaction_type}
