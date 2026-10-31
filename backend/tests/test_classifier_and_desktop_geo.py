import os
import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.computer_vision.classifier import get_product_classifier
from app.database.session import SessionLocal
from app.database.models import User, Merchant, Product

client = TestClient(app)

PROJECT_ROOT = backend_dir.parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
CATALOGUE_DIR = DATA_DIR / "catalogue_images"


def test_product_classifier_direct_classification():
    """Verify that ProductClassifier accurately distinguishes Footwear, Shirts, Electronics, Bags, and Pants."""
    classifier = get_product_classifier()

    # 1. Shoes
    shoe_path = UPLOADS_DIR / "3ed8c488_shoe.jpg"
    if shoe_path.exists():
        img = Image.open(shoe_path)
        pred = classifier.classify_image(img)
        assert pred["category"] == "Footwear & Sneakers", f"Expected Footwear & Sneakers, got {pred['category']}"
        assert pred["confidence"] >= 0.80, f"Expected high confidence, got {pred['confidence']}"
        assert pred["needs_review"] is False

    # 2. White Sneakers
    sneaker_path = UPLOADS_DIR / "06567380_white_sneakers.jpg"
    if sneaker_path.exists():
        img = Image.open(sneaker_path)
        pred = classifier.classify_image(img)
        assert pred["category"] == "Footwear & Sneakers", f"Expected Footwear & Sneakers, got {pred['category']}"
        assert pred["confidence"] >= 0.80

    # 3. Casual Shirt
    shirt_path = UPLOADS_DIR / "31227119_casual_shirt.jpg"
    if shirt_path.exists():
        img = Image.open(shirt_path)
        pred = classifier.classify_image(img)
        assert pred["category"] == "Casual Shirts", f"Expected Casual Shirts, got {pred['category']}"
        assert pred["confidence"] >= 0.80
        assert pred["needs_review"] is False

    # 4. Headphones / Electronics
    audio_path = UPLOADS_DIR / "2f499e87_headphones.jpg"
    if audio_path.exists():
        img = Image.open(audio_path)
        pred = classifier.classify_image(img)
        assert pred["category"] == "Electronics", f"Expected Electronics, got {pred['category']}"
        assert pred["confidence"] >= 0.80

    # 5. Bag / Accessories
    bag_path = CATALOGUE_DIR / "product_1.jpg"
    if bag_path.exists():
        img = Image.open(bag_path)
        pred = classifier.classify_image(img)
        assert pred["category"] in ["Accessories & Bags", "Accessories"], f"Expected Accessories, got {pred['category']}"

    # 6. Trousers / Pants
    trouser_path = UPLOADS_DIR / "sample_trousers.jpg"
    if trouser_path.exists():
        img = Image.open(trouser_path)
        pred = classifier.classify_image(img)
        assert pred["category"] == "Trousers & Pants", f"Expected Trousers & Pants, got {pred['category']}"


def test_api_upload_shoe_never_classified_as_casual_shirt():
    """Verify that uploading a shoe image produces Footwear & Sneakers and retrieves footwear alternatives."""
    shoe_path = UPLOADS_DIR / "3ed8c488_shoe.jpg"
    if not shoe_path.exists():
        shoe_path = UPLOADS_DIR / "06567380_white_sneakers.jpg"
    
    assert shoe_path.exists(), "Shoe test image must exist"

    with open(shoe_path, "rb") as f:
        response = client.post(
            "/api/videos/upload",
            files={"file": ("test_shoe.jpg", f, "image/jpeg")},
            data={"title": "Verification Red Sports Shoe", "description": "Testing category accuracy"}
        )

    assert response.status_code == 200, f"Upload failed: {response.text}"
    data = response.json()

    # The primary category must NOT be Casual Shirts
    assert data["primary_category"] != "Casual Shirts", "Shoe image was incorrectly classified as Casual Shirts!"
    assert data["primary_category"] == "Footwear & Sneakers", f"Expected Footwear & Sneakers, got {data['primary_category']}"
    assert data["confidence"] >= 0.70
    assert data["needs_review"] is False
    assert data["classifier_engine"] in ["open_clip_vit_b32", "open_clip", "resnet18_imagenet"]

    # Ingestion results: similar items must prioritize footwear
    similar_items = data.get("similar_products") or data.get("similar_items", [])
    if similar_items:
        # At least the top retrieved item should be footwear
        top_cat = similar_items[0].get("category")
        assert top_cat == "Footwear & Sneakers", f"Expected top similar item to be Footwear & Sneakers, got {top_cat}"


def test_api_upload_casual_shirt_classified_correctly():
    """Verify that uploading a casual shirt image correctly produces Casual Shirts and retrieves shirts."""
    shirt_path = UPLOADS_DIR / "31227119_casual_shirt.jpg"
    assert shirt_path.exists(), "Shirt test image must exist"

    with open(shirt_path, "rb") as f:
        response = client.post(
            "/api/videos/upload",
            files={"file": ("test_shirt.jpg", f, "image/jpeg")},
            data={"title": "Verification Blue Denim Shirt", "description": "Testing shirt category"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["primary_category"] in ["Casual Shirts", "Polo T-Shirts"]
    assert data["confidence"] >= 0.70

    similar_items = data.get("similar_products") or data.get("similar_items", [])
    if similar_items:
        top_cat = similar_items[0].get("category")
        assert top_cat in ["Casual Shirts", "Polo T-Shirts"], f"Expected shirt category, got {top_cat}"


def test_device_location_api_endpoint():
    """Verify the /api/location/device-ip endpoint behavior."""
    response = client.get("/api/location/device-ip")
    # If online, it returns 200 with real IP geolocation; if offline, 503 with honest explanation
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert -90.0 <= data["latitude"] <= 90.0
        assert -180.0 <= data["longitude"] <= 180.0
        assert data["city"]
        assert data["source"] == "network_ip"
    else:
        detail = response.json().get("detail", "")
        assert "Windows Settings" in detail or "select your city manually" in detail


def test_database_and_packaged_binary_integrity():
    """Ensure that the production SQLite database, merchants, and release assets are intact."""
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        merchant_count = db.query(Merchant).count()
        product_count = db.query(Product).count()

        assert user_count >= 30, f"Expected >= 30 users, found {user_count}"
        assert merchant_count >= 20, f"Expected >= 20 merchants, found {merchant_count}"
        assert product_count >= 50, f"Expected >= 50 products, found {product_count}"
    finally:
        db.close()

    # Verify existing packaged dist is protected
    dist_dir = PROJECT_ROOT / "dist"
    if dist_dir.exists():
        exe_file = dist_dir / "Scrollix AI-win32-x64" / "Scrollix AI.exe"
        assert exe_file.exists(), "Packaged executable in dist/Scrollix AI-win32-x64/Scrollix AI.exe must remain preserved"
