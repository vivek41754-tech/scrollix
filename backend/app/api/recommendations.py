from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User, Video, Product, Interaction
from app.api.auth import get_current_user
from app.services.recommendations.recommender import recommender

router = APIRouter(prefix="/recommendations", tags=["Recommendation Feed"])

@router.get("/feed")
def get_recommendations_feed(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    limit: int = Query(15),
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = user.id if user else None
    results = recommender.get_recommended_feed(
        db=db,
        user_id=user_id,
        user_lat=lat,
        user_lng=lng,
        limit=limit
    )
    return results

@router.get("/videos")
def get_recommended_videos(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns short-form video feed with real detection overlays and shop links.
    """
    videos = db.query(Video).order_by(Video.created_at.desc()).all()
    feed_items = []

    for v in videos:
        detections = v.get_detections()
        enriched_detections = []
        featured_products = []

        for d in detections:
            p_id = d.get("product_id")
            if p_id:
                p = db.query(Product).filter(Product.id == p_id).first()
                if p:
                    prod_summary = {
                        "id": p.id,
                        "title": p.title,
                        "price": p.price,
                        "category": p.category,
                        "image_url": p.image_url,
                        "merchant_name": p.merchant.business_name if p.merchant else "Local Store",
                        "merchant_city": p.merchant.city if p.merchant else "Local",
                        "merchant_verified": p.merchant.is_verified if p.merchant else False,
                        "merchant_trust_score": p.merchant.trust_score if p.merchant else 75.0,
                    }
                    d_enriched = d.copy()
                    d_enriched["product_info"] = prod_summary
                    enriched_detections.append(d_enriched)
                    if prod_summary not in featured_products:
                        featured_products.append(prod_summary)
            else:
                enriched_detections.append(d)

        feed_items.append({
            "id": v.id,
            "title": v.title,
            "description": v.description,
            "video_url": v.video_url,
            "thumbnail_url": v.thumbnail_url,
            "duration": v.duration,
            "detections": enriched_detections,
            "featured_products": featured_products,
            "created_at": v.created_at.isoformat() if v.created_at else None
        })

    return feed_items
