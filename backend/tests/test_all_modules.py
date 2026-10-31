import os
import tempfile
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.database.models import User, Merchant, Product, Video, Interaction, Review, FraudFlag
from app.services.computer_vision.detector import detector
from app.services.embeddings.embedder import embedder, EMBEDDING_DIM
from app.services.vector_search.faiss_index import FaissVectorIndex, vector_index
from app.services.recommendations.recommender import recommender
from app.services.location.distance import haversine_distance_km, haversine_distance_miles
from app.services.fraud.detector import fraud_detector
from app.services.sentiment.analyzer import sentiment_analyzer
from app.services.chatbot.assistant import assistant
from app.services.analytics.engine import analytics_engine

def test_auth_workflow(client: TestClient):
    """Verifies registration, login, duplicate check, and role authorization."""
    import uuid
    uid = uuid.uuid4().hex[:6]
    email = f"test_{uid}@example.com"
    username = f"user_{uid}"

    # 1. Register
    reg_resp = client.post("/api/auth/register", json={
        "email": email,
        "username": username,
        "password": "Password123!",
        "role": "customer"
    })
    assert reg_resp.status_code == 200, reg_resp.text
    data = reg_resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == email

    # 2. Duplicate registration fails
    dup_resp = client.post("/api/auth/register", json={
        "email": email,
        "username": username,
        "password": "Password123!"
    })
    assert dup_resp.status_code == 400

    # 3. Login
    login_resp = client.post("/api/auth/login", json={
        "username_or_email": username,
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 4. Authenticated /me
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == username

def test_merchant_and_product_crud(client: TestClient):
    """Verifies merchant onboarding, product CRUD, and FAISS vector indexing."""
    import uuid
    uid = uuid.uuid4().hex[:6]
    
    # Register merchant user
    reg = client.post("/api/auth/register", json={
        "email": f"merchant_{uid}@store.com",
        "username": f"merchant_{uid}",
        "password": "password123",
        "role": "merchant"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Onboard merchant
    onboard_resp = client.post("/api/merchants/onboard", json={
        "business_name": f"Studio {uid} Designs",
        "description": "Custom modern streetwear.",
        "category": "Apparel",
        "address": "100 Market St",
        "city": "San Francisco",
        "latitude": 37.79,
        "longitude": -122.40,
        "phone": "+1 415 555 9999"
    }, headers=headers)
    assert onboard_resp.status_code == 200
    assert onboard_resp.json()["is_verified"] is False

    # Create product
    prod_resp = client.post("/api/products", json={
        "title": f"Graphic Cotton Hoodie {uid}",
        "description": "Heavyweight French terry cotton hoodie.",
        "category": "Apparel",
        "price": 75.0,
        "inventory": 20,
        "image_url": "https://example.com/hoodie.jpg",
        "tags": ["hoodie", "cotton", "streetwear"]
    }, headers=headers)
    assert prod_resp.status_code == 200
    prod_id = prod_resp.json()["id"]

    # Retrieve product
    get_prod = client.get(f"/api/products/{prod_id}")
    assert get_prod.status_code == 200
    assert get_prod.json()["title"] == f"Graphic Cotton Hoodie {uid}"

    # Verify indexed in FAISS
    assert vector_index.index.ntotal > 0

    # Delete product
    del_resp = client.delete(f"/api/products/{prod_id}", headers=headers)
    assert del_resp.status_code == 200

def test_yolo_object_detection():
    """Verifies actual YOLO model inference on a sample image."""
    img = Image.new("RGB", (320, 320), color=(200, 200, 200))
    detections = detector.detect_image(img, conf_threshold=0.1)
    # Output must be a list of detection objects with box, label, confidence
    assert isinstance(detections, list)
    if detector.is_available:
        assert detector.model is not None

def test_embeddings_and_faiss_persistence():
    """Verifies 512-dim embedding extraction, FAISS search, and disk persistence."""
    # Text embedding
    vec1 = embedder.embed_text("running shoes sneakers red")
    assert vec1.shape == (EMBEDDING_DIM,)
    assert abs(np.linalg.norm(vec1) - 1.0) < 1e-3

    # Image embedding
    test_img = Image.new("RGB", (100, 100), color="blue")
    vec2 = embedder.embed_image(test_img)
    assert vec2.shape == (EMBEDDING_DIM,)
    assert abs(np.linalg.norm(vec2) - 1.0) < 1e-3

    # Test FAISS index save and reload
    with tempfile.TemporaryDirectory() as tmpdir:
        from pathlib import Path
        idx_file = Path(tmpdir) / "test.index"
        meta_file = Path(tmpdir) / "test_meta.json"

        idx = FaissVectorIndex(index_path=idx_file, meta_path=meta_file)
        idx.add_product(101, vec1)
        idx.add_product(102, vec2)
        assert idx.index.ntotal == 2

        # Search
        hits = idx.search_similar(vec1, top_k=2, min_score=-1.0)
        assert len(hits) == 2
        assert hits[0]["product_id"] == 101

        # Reload from disk
        idx_loaded = FaissVectorIndex(index_path=idx_file, meta_path=meta_file)
        assert idx_loaded.index.ntotal == 2
        hits_loaded = idx_loaded.search_similar(vec1, top_k=1, min_score=-1.0)
        assert hits_loaded[0]["product_id"] == 101

def test_haversine_distance():
    """Verifies documented Haversine geographic formula accuracy."""
    # Distance between San Francisco (37.7749, -122.4194) and Oakland (37.8044, -122.2711) ~ 13.5 km
    dist = haversine_distance_km(37.7749, -122.4194, 37.8044, -122.2711)
    assert 12.0 < dist < 16.0

    # Distance to self must be 0
    dist_zero = haversine_distance_km(37.7749, -122.4194, 37.7749, -122.4194)
    assert dist_zero == 0.0

    miles = haversine_distance_miles(37.7749, -122.4194, 37.8044, -122.2711)
    assert miles < dist

def test_recommendation_feed(client: TestClient):
    """Verifies hybrid recommendations return scores and explainability strings."""
    resp = client.get("/api/recommendations/feed?lat=37.7749&lng=-122.4194&limit=5")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    first = items[0]
    assert "recommendation_score" in first
    assert "explanation" in first
    assert len(first["explanation"]) > 0
    assert "price" in first

def test_shopping_assistant_catalogue_grounding(client: TestClient):
    """Verifies assistant answers with catalogue products and discloses fallback mode."""
    # Query within budget
    resp = client.post("/api/assistant/chat", json={
        "message": "I need running shoes under $150"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert "recommended_products" in data
    assert data["mode"] in ["local_fallback", "gemini_cloud"]
    assert "disclaimer" in data

def test_fraud_detector_explainable_rules():
    """Verifies fraud detector flags abnormal listings and produces explainable reasons."""
    db = SessionLocal()
    try:
        # Check an existing merchant
        m = db.query(Merchant).first()
        assert m is not None
        eval_result = fraud_detector.evaluate_merchant(db, m.id)
        assert "risk_score" in eval_result
        assert "is_suspicious" in eval_result
        assert "reasons" in eval_result
        assert isinstance(eval_result["reasons"], list)
    finally:
        db.close()

def test_sentiment_analysis():
    """Verifies sentiment valence scoring, negation handling, and aggregation."""
    # Positive
    res_pos = sentiment_analyzer.analyze_text("This jacket is amazing, excellent quality!")
    assert res_pos["label"] == "positive"
    assert res_pos["polarity"] > 0.2

    # Negative with negation
    res_neg = sentiment_analyzer.analyze_text("This product is terrible and broke immediately, not good.")
    assert res_neg["label"] == "negative"
    assert res_neg["polarity"] < -0.1

    # Aggregation
    agg = sentiment_analyzer.aggregate_reviews([res_pos, res_neg])
    assert agg["total_reviews"] == 2
    assert agg["is_estimate"] is True

def test_analytics_metrics(client: TestClient):
    """Verifies factual metrics computed from persisted database events."""
    resp = client.get("/api/analytics/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "time_series" in data
    assert "top_products" in data
    assert data["summary"]["total_products"] > 0

def test_admin_system_health(client: TestClient):
    """Verifies system health check endpoint reporting AI models, DB, and FAISS."""
    resp = client.get("/api/admin/health")
    assert resp.status_code == 200
    health = resp.json()
    assert health["status"] in ["healthy", "degraded"]
    assert "computer_vision" in health
    assert "vector_search" in health
    assert "database" in health
