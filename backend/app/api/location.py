from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Merchant, Product
from app.services.location.distance import (
    haversine_distance_km,
    haversine_distance_miles,
    PRESET_CITIES
)

router = APIRouter(prefix="/location", tags=["Location Intelligence"])

@router.get("/cities")
def get_preset_cities():
    """Returns list of supported preset cities with coordinates for manual location entry."""
    return [
        {"city": name, "latitude": coords["lat"], "longitude": coords["lng"]}
        for name, coords in PRESET_CITIES.items()
    ]

@router.get("/reverse-geocode")
def reverse_geocode(
    lat: float = Query(..., description="Latitude (-90.0 to 90.0)"),
    lng: float = Query(..., description="Longitude (-180.0 to 180.0)")
):
    """
    Resolves latitude and longitude coordinates to a city/area name.
    First checks proximity to preset cities. If none match, attempts lightweight reverse geocoding,
    falling back gracefully to 'Current device location' without crashing or returning arbitrary cities.
    """
    if not (-90.0 <= lat <= 90.0):
        raise HTTPException(status_code=400, detail="Latitude must be between -90.0 and 90.0 degrees.")
    if not (-180.0 <= lng <= 180.0):
        raise HTTPException(status_code=400, detail="Longitude must be between -180.0 and 180.0 degrees.")

    # 1. Check proximity to preset cities (within 25 km)
    for city_name, coords in PRESET_CITIES.items():
        d = haversine_distance_km(lat, lng, coords["lat"], coords["lng"])
        if d <= 25.0:
            return {
                "city": city_name,
                "display_name": f"{city_name} (approx. {d:.1f} km from center)",
                "latitude": lat,
                "longitude": lng,
                "match_type": "preset",
                "distance_to_center_km": d
            }

    # 2. Attempt reverse geocoding via Nominatim with short timeout
    try:
        import urllib.request
        import json
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&zoom=10"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ScrollixAI-Desktop/1.0 (local-app)"}
        )
        with urllib.request.urlopen(req, timeout=1.5) as response:
            data = json.loads(response.read().decode("utf-8"))
            addr = data.get("address", {})
            detected_name = (
                addr.get("city")
                or addr.get("town")
                or addr.get("municipality")
                or addr.get("county")
                or addr.get("state")
                or data.get("name")
            )
            if detected_name:
                return {
                    "city": detected_name,
                    "display_name": data.get("display_name", detected_name),
                    "latitude": lat,
                    "longitude": lng,
                    "match_type": "geocoded"
                }
    except Exception:
        pass

    # 3. Graceful fallback to coordinate label
    coord_label = f"{lat:.4f}, {lng:.4f}"
    return {
        "city": "Current device location",
        "display_name": f"Current device location ({coord_label})",
        "latitude": lat,
        "longitude": lng,
        "match_type": "coordinates"
    }

@router.get("/device-ip")
def get_device_location_by_ip():
    """
    Retrieves the actual device geographic location based on network IP geolocation.
    Returns the real detected coordinates and city without hardcoded fallbacks or faked GPS positions.
    Raises HTTPException(503) if network geolocation services are unreachable (e.g. offline).
    """
    import urllib.request
    import json

    services = [
        ("http://ip-api.com/json/?fields=status,message,country,regionName,city,lat,lon,query", "ip-api"),
        ("https://ipapi.co/json/", "ipapi")
    ]

    for service_url, provider in services:
        try:
            req = urllib.request.Request(
                service_url,
                headers={"User-Agent": "ScrollixAI-Desktop/1.0"}
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if provider == "ip-api" and data.get("status") == "success":
                    lat = float(data.get("lat"))
                    lon = float(data.get("lon"))
                    city = data.get("city") or data.get("regionName") or "Current device location"
                    return {
                        "latitude": round(lat, 6),
                        "longitude": round(lon, 6),
                        "city": city,
                        "source": "network_ip",
                        "provider": provider
                    }
                elif provider == "ipapi" and "latitude" in data and "longitude" in data:
                    lat = float(data["latitude"])
                    lon = float(data["longitude"])
                    city = data.get("city") or data.get("region") or "Current device location"
                    return {
                        "latitude": round(lat, 6),
                        "longitude": round(lon, 6),
                        "city": city,
                        "source": "network_ip",
                        "provider": provider
                    }
        except Exception:
            continue

    raise HTTPException(
        status_code=503,
        detail="Device network geolocation is currently unavailable. Please verify network access, enable Windows Location Services in Settings > Privacy & security > Location, or select your city manually."
    )

@router.get("/nearby-merchants")
def get_nearby_merchants(
    lat: float = Query(..., description="User latitude (-90.0 to 90.0)"),
    lng: float = Query(..., description="User longitude (-180.0 to 180.0)"),
    radius_km: float = Query(25.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    if not (-90.0 <= lat <= 90.0):
        raise HTTPException(status_code=400, detail="Latitude must be between -90.0 and 90.0 degrees.")
    if not (-180.0 <= lng <= 180.0):
        raise HTTPException(status_code=400, detail="Longitude must be between -180.0 and 180.0 degrees.")
    if radius_km <= 0:
        raise HTTPException(status_code=400, detail="Search radius must be greater than 0 km.")

    merchants = db.query(Merchant).all()
    results = []
    all_distances = []

    for m in merchants:
        if m.latitude is None or m.longitude is None:
            continue

        dist_km = haversine_distance_km(lat, lng, m.latitude, m.longitude)
        all_distances.append(dist_km)

        if dist_km <= radius_km:
            results.append({
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
                "distance_km": dist_km,
                "distance_miles": haversine_distance_miles(lat, lng, m.latitude, m.longitude),
                "products_count": len([p for p in m.products if p.is_active])
            })

    results.sort(key=lambda x: x["distance_km"])
    nearest_dist = min(all_distances) if all_distances else None

    return {
        "user_coordinates": {"latitude": lat, "longitude": lng},
        "search_radius_km": radius_km,
        "total_merchants_found": len(results),
        "merchants": results,
        "nearest_distance_km": round(nearest_dist, 2) if nearest_dist is not None else None
    }

@router.get("/nearby-products")
def get_nearby_products(
    lat: float = Query(..., description="User latitude (-90.0 to 90.0)"),
    lng: float = Query(..., description="User longitude (-180.0 to 180.0)"),
    radius_km: float = Query(25.0, description="Search radius in kilometers"),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    if not (-90.0 <= lat <= 90.0):
        raise HTTPException(status_code=400, detail="Latitude must be between -90.0 and 90.0 degrees.")
    if not (-180.0 <= lng <= 180.0):
        raise HTTPException(status_code=400, detail="Longitude must be between -180.0 and 180.0 degrees.")
    if radius_km <= 0:
        raise HTTPException(status_code=400, detail="Search radius must be greater than 0 km.")

    products = db.query(Product).filter(Product.is_active == True).all()
    results = []

    for p in products:
        if not p.merchant or p.merchant.latitude is None or p.merchant.longitude is None:
            continue
        if category and category.lower() not in p.category.lower():
            continue

        dist_km = haversine_distance_km(lat, lng, p.merchant.latitude, p.merchant.longitude)
        if dist_km <= radius_km:
            results.append({
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "category": p.category,
                "price": p.price,
                "image_url": p.image_url,
                "merchant_id": p.merchant.id,
                "merchant_name": p.merchant.business_name,
                "merchant_address": p.merchant.address,
                "merchant_city": p.merchant.city,
                "merchant_verified": p.merchant.is_verified,
                "merchant_trust_score": p.merchant.trust_score,
                "distance_km": dist_km
            })

    results.sort(key=lambda x: x["distance_km"])
    return results

def calculate_destination_point(lat: float, lng: float, dist_km: float, bearing_deg: float) -> tuple[float, float]:
    """
    Calculates destination coordinates given start point, distance (km), and bearing (degrees)
    using spherical earth geometry.
    """
    import math
    from app.services.location.distance import EARTH_RADIUS_KM

    r = EARTH_RADIUS_KM
    delta = dist_km / r
    theta = math.radians(bearing_deg)
    phi1 = math.radians(lat)
    lambda1 = math.radians(lng)

    phi2 = math.asin(math.sin(phi1) * math.cos(delta) + math.cos(phi1) * math.sin(delta) * math.cos(theta))
    lambda2 = lambda1 + math.atan2(math.sin(theta) * math.sin(delta) * math.cos(phi1), math.cos(delta) - math.sin(phi1) * math.sin(phi2))

    lat2 = math.degrees(phi2)
    lng2 = (math.degrees(lambda2) + 540) % 360 - 180
    return round(lat2, 6), round(lng2, 6)

@router.post("/seed-nearby-demo")
def seed_nearby_demo_merchants(
    lat: float = Query(..., description="Reference latitude (-90.0 to 90.0)"),
    lng: float = Query(..., description="Reference longitude (-180.0 to 180.0)"),
    city: Optional[str] = Query(None, description="Optional city or area name"),
    db: Session = Depends(get_db)
):
    """
    Idempotently seeds or positions 3 clearly labelled demonstration merchants at distances
    strictly between 10 and 20 km from the user's valid reference coordinates.
    """
    if not (-90.0 <= lat <= 90.0):
        raise HTTPException(status_code=400, detail="Latitude must be between -90.0 and 90.0 degrees.")
    if not (-180.0 <= lng <= 180.0):
        raise HTTPException(status_code=400, detail="Longitude must be between -180.0 and 180.0 degrees.")

    from app.database.models import User
    from app.core.security import get_password_hash
    from app.services.vector_search.faiss_index import vector_index
    from app.services.embeddings.embedder import embedder

    # Target distances strictly between 10 and 20 km
    demo_configs = [
        {
            "username": "demo_nearby_1",
            "email": "nearby1@scrollix-demo.ai",
            "business_name": "[Demo] Horizon Athletic Hub",
            "category": "Footwear & Sneakers",
            "description": "[Demo Merchant] Demonstration sports footwear, trail runners, and cushioned training sneakers located ~12 km from your reference location.",
            "phone": "+1 (555) 012-3401",
            "trust_score": 93.0,
            "target_dist_km": 11.8,
            "bearing_deg": 35.0,
            "products": [
                {
                    "title": "[Demo] AeroPace Carbon Road Runners",
                    "category": "Footwear & Sneakers",
                    "price": 4499.0,
                    "inventory": 25,
                    "description": "Lightweight carbon-plated demonstration running shoes with responsive foam.",
                    "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
                    "tags": ["shoes", "sneakers", "running", "athletic"]
                },
                {
                    "title": "[Demo] TrailGrip All-Weather Hiking Shoes",
                    "category": "Footwear & Sneakers",
                    "price": 3799.0,
                    "inventory": 18,
                    "description": "Demonstration all-terrain outdoor trail shoes with waterproof membrane.",
                    "image_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600",
                    "tags": ["shoes", "hiking", "outdoor", "trail"]
                }
            ]
        },
        {
            "username": "demo_nearby_2",
            "email": "nearby2@scrollix-demo.ai",
            "business_name": "[Demo] Metro Stitch Tailors",
            "category": "Apparel & Shirts",
            "description": "[Demo Merchant] Demonstration classic-fit polo shirts, casual cotton button-downs, and apparel located ~15 km from your reference location.",
            "phone": "+1 (555) 012-3402",
            "trust_score": 91.5,
            "target_dist_km": 14.5,
            "bearing_deg": 155.0,
            "products": [
                {
                    "title": "[Demo] Pique Breathable Cotton Polo T-Shirt",
                    "category": "Polo T-Shirts",
                    "price": 1299.0,
                    "inventory": 40,
                    "description": "Classic ribbed-collar demonstration polo crafted from breathable combed cotton.",
                    "image_url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=600",
                    "tags": ["polo", "shirt", "cotton", "casual"]
                },
                {
                    "title": "[Demo] Vintage Chambray Casual Shirt",
                    "category": "Casual Shirts",
                    "price": 1699.0,
                    "inventory": 30,
                    "description": "Comfort-fit demonstration casual chambray button-down shirt for everyday wear.",
                    "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600",
                    "tags": ["shirt", "casual", "chambray", "apparel"]
                }
            ]
        },
        {
            "username": "demo_nearby_3",
            "email": "nearby3@scrollix-demo.ai",
            "business_name": "[Demo] NovaPulse Tech Depot",
            "category": "Electronics",
            "description": "[Demo Merchant] Demonstration wireless audio, noise-cancelling headphones, and peripheral gear located ~18 km from your reference location.",
            "phone": "+1 (555) 012-3403",
            "trust_score": 95.0,
            "target_dist_km": 17.6,
            "bearing_deg": 265.0,
            "products": [
                {
                    "title": "[Demo] PureAcoustic ANC Wireless Headphones",
                    "category": "Electronics",
                    "price": 5999.0,
                    "inventory": 15,
                    "description": "Demonstration active noise cancelling studio-grade over-ear wireless headphones.",
                    "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600",
                    "tags": ["headphones", "audio", "wireless", "electronics"]
                },
                {
                    "title": "[Demo] BassPulse Low-Latency Earbuds",
                    "category": "Electronics",
                    "price": 2299.0,
                    "inventory": 35,
                    "description": "True wireless demonstration earbuds with ultra-low latency audio profile.",
                    "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600",
                    "tags": ["earbuds", "audio", "wireless", "electronics"]
                }
            ]
        }
    ]

    city_label = city or "Local Vicinity"
    results = []

    for cfg in demo_configs:
        m_lat, m_lng = calculate_destination_point(lat, lng, cfg["target_dist_km"], cfg["bearing_deg"])
        actual_dist_km = haversine_distance_km(lat, lng, m_lat, m_lng)

        # 1. Upsert demo user
        user = db.query(User).filter(User.username == cfg["username"]).first()
        if not user:
            user = User(
                username=cfg["username"],
                email=cfg["email"],
                hashed_password=get_password_hash("demo123"),
                role="merchant",
                avatar_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 2. Upsert merchant profile
        merchant = db.query(Merchant).filter(Merchant.user_id == user.id).first()
        if not merchant:
            merchant = Merchant(
                user_id=user.id,
                business_name=cfg["business_name"],
                category=cfg["category"],
                description=cfg["description"],
                address=f"Demo Location (~{actual_dist_km:.1f} km from reference)",
                city=city_label,
                latitude=m_lat,
                longitude=m_lng,
                phone=cfg["phone"],
                is_verified=True,
                trust_score=cfg["trust_score"]
            )
            db.add(merchant)
            db.commit()
            db.refresh(merchant)
        else:
            merchant.business_name = cfg["business_name"]
            merchant.latitude = m_lat
            merchant.longitude = m_lng
            merchant.city = city_label
            merchant.address = f"Demo Location (~{actual_dist_km:.1f} km from reference)"
            merchant.description = cfg["description"]
            db.commit()
            db.refresh(merchant)

        # 3. Upsert products
        for p_cfg in cfg["products"]:
            prod = db.query(Product).filter(
                Product.merchant_id == merchant.id,
                Product.title == p_cfg["title"]
            ).first()
            if not prod:
                prod = Product(
                    merchant_id=merchant.id,
                    title=p_cfg["title"],
                    description=p_cfg["description"],
                    category=p_cfg["category"],
                    price=p_cfg["price"],
                    inventory=p_cfg["inventory"],
                    image_url=p_cfg["image_url"]
                )
                prod.set_tags(p_cfg["tags"])
                db.add(prod)
                db.commit()
                db.refresh(prod)
                try:
                    vec = embedder.embed_text(f"{prod.title} {prod.category} {prod.description}")
                    vector_index.add_product(prod.id, vec)
                    prod.embedding_id = prod.id
                    db.commit()
                except Exception:
                    pass

        results.append({
            "id": merchant.id,
            "business_name": merchant.business_name,
            "category": merchant.category,
            "city": merchant.city,
            "latitude": merchant.latitude,
            "longitude": merchant.longitude,
            "target_distance_km": cfg["target_dist_km"],
            "distance_km": actual_dist_km,
            "is_within_10_20_km": 10.0 <= actual_dist_km <= 20.0,
            "products_count": len([p for p in merchant.products if p.is_active])
        })

    return {
        "message": "Successfully seeded 3 demo merchants at verified 10-20 km distance from reference location.",
        "reference_location": {"latitude": lat, "longitude": lng, "city": city_label},
        "merchants": results
    }

