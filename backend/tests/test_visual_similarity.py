import os
import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend is on sys.path
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app
from app.core.config import settings
from app.database.session import SessionLocal
from app.database.models import Product
from app.services.vector_search.faiss_index import vector_index
from app.services.embeddings.embedder import embedder

client = TestClient(app)

def test_visual_faiss_catalogue_indexed():
    """Verify that all 56 catalogue products are indexed in FAISS with visual embeddings."""
    db = SessionLocal()
    try:
        active_prods = db.query(Product).filter(Product.is_active == True).all()
        assert len(active_prods) >= 50, f"Expected at least 50 active products, found {len(active_prods)}"
        assert vector_index.index.ntotal >= len(active_prods), (
            f"FAISS index count ({vector_index.index.ntotal}) must match or exceed active products ({len(active_prods)})"
        )
        assert len(vector_index.color_histograms) >= len(active_prods), (
            f"Color profiles ({len(vector_index.color_histograms)}) must match active products ({len(active_prods)})"
        )
    finally:
        db.close()

def test_red_sports_shoe_recognition():
    """
    Test uploading a photograph of a red sports shoe.
    Must identify category 'Footwear & Sneakers' and retrieve similar athletic footwear from catalogue.
    """
    img_path = settings.DATA_DIR / "catalogue_images" / "product_3.jpg"
    assert img_path.exists(), f"Benchmark image {img_path} not found"

    with open(img_path, "rb") as f:
        res = client.post(
            "/api/videos/upload",
            files={"file": ("red_running_shoe.jpg", f, "image/jpeg")},
            data={"title": "Red Sports Shoe Pipeline Test", "description": "Athletic footwear visual test"}
        )

    assert res.status_code == 200, f"Upload failed: {res.text}"
    data = res.json()
    assert data.get("detections_count", 0) > 0, "Expected at least 1 detection"
    assert data.get("recognized_category") == "Footwear & Sneakers", (
        f"Expected category 'Footwear & Sneakers', got '{data.get('recognized_category')}'"
    )

    similar = data.get("similar_products", [])
    assert len(similar) > 0, "Expected ranked visually similar products"
    # Verify top similar product is footwear
    top_p = similar[0]
    assert top_p["category"] == "Footwear & Sneakers", f"Top match category should be Footwear, got {top_p['category']}"
    assert top_p["similarity_score"] >= 0.50, f"Similarity score should be >= 0.50, got {top_p['similarity_score']}"
    print(f"Red shoe matched: {top_p['title']} ({top_p['category']}) with score {top_p['similarity_score']}")

def test_polo_shirt_recognition():
    """
    Test uploading a photograph of a polo shirt.
    Must identify category 'Polo T-Shirts' and retrieve similar polo shirts from catalogue.
    """
    img_path = settings.DATA_DIR / "catalogue_images" / "product_52.jpg"
    assert img_path.exists(), f"Benchmark image {img_path} not found"

    with open(img_path, "rb") as f:
        res = client.post(
            "/api/videos/upload",
            files={"file": ("polo_shirt.jpg", f, "image/jpeg")},
            data={"title": "Polo Shirt Pipeline Test", "description": "Polo shirt visual test"}
        )

    assert res.status_code == 200, f"Upload failed: {res.text}"
    data = res.json()
    assert data.get("recognized_category") == "Polo T-Shirts", (
        f"Expected category 'Polo T-Shirts', got '{data.get('recognized_category')}'"
    )

    similar = data.get("similar_products", [])
    assert len(similar) > 0, "Expected similar polo shirts"
    top_p = similar[0]
    assert top_p["category"] == "Polo T-Shirts"
    print(f"Polo shirt matched: {top_p['title']} ({top_p['category']}) with score {top_p['similarity_score']}")

def test_casual_shirt_recognition():
    """
    Test uploading a photograph of a casual shirt.
    Must identify category 'Casual Shirts' and retrieve similar casual shirts from catalogue.
    """
    img_path = settings.DATA_DIR / "catalogue_images" / "product_31.jpg"
    assert img_path.exists(), f"Benchmark image {img_path} not found"

    with open(img_path, "rb") as f:
        res = client.post(
            "/api/videos/upload",
            files={"file": ("casual_shirt.jpg", f, "image/jpeg")},
            data={"title": "Casual Shirt Pipeline Test", "description": "Casual shirt visual test"}
        )

    assert res.status_code == 200, f"Upload failed: {res.text}"
    data = res.json()
    assert data.get("recognized_category") == "Casual Shirts", (
        f"Expected category 'Casual Shirts', got '{data.get('recognized_category')}'"
    )

    similar = data.get("similar_products", [])
    assert len(similar) > 0, "Expected similar casual shirts"
    top_p = similar[0]
    assert top_p["category"] == "Casual Shirts"
    print(f"Casual shirt matched: {top_p['title']} ({top_p['category']}) with score {top_p['similarity_score']}")

def test_wireless_headphones_recognition():
    """
    Test uploading a photograph of wireless headphones.
    Must identify category 'Electronics' and retrieve audio/electronics products.
    """
    img_path = settings.DATA_DIR / "catalogue_images" / "product_19.jpg"
    assert img_path.exists(), f"Benchmark image {img_path} not found"

    with open(img_path, "rb") as f:
        res = client.post(
            "/api/videos/upload",
            files={"file": ("headphones.jpg", f, "image/jpeg")},
            data={"title": "Headphones Pipeline Test", "description": "Electronics audio visual test"}
        )

    assert res.status_code == 200, f"Upload failed: {res.text}"
    data = res.json()
    assert data.get("recognized_category") == "Electronics", (
        f"Expected category 'Electronics', got '{data.get('recognized_category')}'"
    )

    similar = data.get("similar_products", [])
    assert len(similar) > 0, "Expected similar electronics products"
    top_p = similar[0]
    assert top_p["category"] == "Electronics"
    print(f"Headphones matched: {top_p['title']} ({top_p['category']}) with score {top_p['similarity_score']}")

def test_white_sneakers_recognition():
    """
    Test uploading a photograph of white sneakers.
    Must identify category 'Footwear & Sneakers' and retrieve white low-tops/sneakers.
    """
    img_path = settings.DATA_DIR / "catalogue_images" / "product_10.jpg"
    assert img_path.exists(), f"Benchmark image {img_path} not found"

    with open(img_path, "rb") as f:
        res = client.post(
            "/api/videos/upload",
            files={"file": ("white_sneakers.jpg", f, "image/jpeg")},
            data={"title": "White Sneakers Pipeline Test", "description": "White sneaker visual test"}
        )

    assert res.status_code == 200, f"Upload failed: {res.text}"
    data = res.json()
    assert data.get("recognized_category") == "Footwear & Sneakers", (
        f"Expected category 'Footwear & Sneakers', got '{data.get('recognized_category')}'"
    )

    similar = data.get("similar_products", [])
    assert len(similar) > 0, "Expected similar footwear"
    top_p = similar[0]
    assert top_p["category"] == "Footwear & Sneakers"
    print(f"White sneakers matched: {top_p['title']} ({top_p['category']}) with score {top_p['similarity_score']}")

def test_visual_search_endpoint():
    """Test POST /api/search/visual with category and max_price filters."""
    img_path = settings.DATA_DIR / "catalogue_images" / "product_3.jpg"
    with open(img_path, "rb") as f:
        res = client.post(
            "/api/search/visual",
            files={"file": ("search_shoe.jpg", f, "image/jpeg")},
            data={"category": "Footwear", "max_price": 6000.0, "top_k": 5}
        )
    assert res.status_code == 200, f"Visual search failed: {res.text}"
    results = res.json()
    assert len(results) > 0, "Expected at least 1 search result"
    for r in results:
        assert "Footwear" in r["category"]
        assert r["price"] <= 6000.0
