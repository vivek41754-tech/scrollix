from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Merchant, Product, User
from app.api.auth import require_current_user, get_current_user

router = APIRouter(prefix="/merchants", tags=["Merchants"])

class MerchantProfileRequest(BaseModel):
    business_name: str
    description: Optional[str] = ""
    category: Optional[str] = "Retail"
    address: Optional[str] = ""
    city: Optional[str] = ""
    latitude: Optional[float] = 0.0
    longitude: Optional[float] = 0.0
    phone: Optional[str] = ""

@router.get("")
def list_merchants(city: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Merchant)
    if city:
        query = query.filter(Merchant.city.ilike(f"%{city}%"))
    if category:
        query = query.filter(Merchant.category.ilike(f"%{category}%"))
    
    merchants = query.all()
    return [
        {
            "id": m.id,
            "user_id": m.user_id,
            "business_name": m.business_name,
            "description": m.description,
            "category": m.category,
            "address": m.address,
            "city": m.city,
            "latitude": m.latitude,
            "longitude": m.longitude,
            "phone": m.phone,
            "is_verified": m.is_verified,
            "trust_score": m.trust_score,
            "product_count": len(m.products),
            "products_count": len(m.products)
        }
        for m in merchants
    ]

@router.get("/{merchant_id}")
def get_merchant(merchant_id: int, db: Session = Depends(get_db)):
    m = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Merchant not found.")
    
    products = [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "category": p.category,
            "price": p.price,
            "inventory": p.inventory,
            "image_url": p.image_url,
            "tags": p.get_tags()
        }
        for p in m.products if p.is_active
    ]

    return {
        "id": m.id,
        "business_name": m.business_name,
        "description": m.description,
        "category": m.category,
        "address": m.address,
        "city": m.city,
        "latitude": m.latitude,
        "longitude": m.longitude,
        "phone": m.phone,
        "is_verified": m.is_verified,
        "trust_score": m.trust_score,
        "products": products
    }

@router.post("/onboard")
def onboard_merchant(req: MerchantProfileRequest, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    # Check if merchant profile already exists for user
    existing = db.query(Merchant).filter(Merchant.user_id == user.id).first()
    if existing:
        existing.business_name = req.business_name
        existing.description = req.description
        existing.category = req.category
        existing.address = req.address
        existing.city = req.city
        existing.latitude = req.latitude
        existing.longitude = req.longitude
        existing.phone = req.phone
        db.commit()
        db.refresh(existing)
        merchant = existing
    else:
        merchant = Merchant(
            user_id=user.id,
            business_name=req.business_name,
            description=req.description,
            category=req.category,
            address=req.address,
            city=req.city,
            latitude=req.latitude,
            longitude=req.longitude,
            phone=req.phone,
            is_verified=False,
            trust_score=80.0
        )
        user.role = "merchant"
        db.add(merchant)
        db.commit()
        db.refresh(merchant)

    return {
        "id": merchant.id,
        "business_name": merchant.business_name,
        "is_verified": merchant.is_verified,
        "trust_score": merchant.trust_score,
        "message": "Merchant profile saved successfully."
    }
