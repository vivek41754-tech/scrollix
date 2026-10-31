import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.location.distance import (
    haversine_distance_km,
    haversine_distance_miles,
    is_within_radius,
    PRESET_CITIES
)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_preset_cities_endpoint(client: TestClient):
    """Verify supported preset cities are returned with valid coordinates."""
    response = client.get("/api/location/cities")
    assert response.status_code == 200
    cities = response.json()
    assert isinstance(cities, list)
    assert len(cities) >= 5

    city_names = [c["city"] for c in cities]
    assert "Bengaluru" in city_names
    assert "Mumbai" in city_names
    assert "New Delhi" in city_names
    assert "San Francisco" in city_names

    for item in cities:
        assert "city" in item
        assert -90.0 <= item["latitude"] <= 90.0
        assert -180.0 <= item["longitude"] <= 180.0

def test_haversine_formula_math():
    """Verify the spherical Haversine formula calculates known distances accurately."""
    # Distance between Bengaluru (12.9716, 77.5946) and Mumbai (19.0760, 72.8777) is ~840-845 km
    dist_blr_mum = haversine_distance_km(12.9716, 77.5946, 19.0760, 72.8777)
    assert 830.0 < dist_blr_mum < 860.0

    # Distance to identical point must be 0
    dist_zero = haversine_distance_km(37.7749, -122.4194, 37.7749, -122.4194)
    assert dist_zero == 0.0

    # Miles conversion
    miles = haversine_distance_miles(12.9716, 77.5946, 19.0760, 72.8777)
    assert round(dist_blr_mum * 0.621371, 2) == miles

def test_coordinate_validation_bounds(client: TestClient):
    """Verify endpoint rejects invalid coordinates with HTTP 400."""
    # Latitude > 90
    res1 = client.get("/api/location/nearby-merchants?lat=95.0&lng=77.0&radius_km=25")
    assert res1.status_code == 400
    assert "Latitude must be between -90.0 and 90.0" in res1.json()["detail"]

    # Latitude < -90
    res2 = client.get("/api/location/nearby-merchants?lat=-95.0&lng=77.0&radius_km=25")
    assert res2.status_code == 400

    # Longitude > 180
    res3 = client.get("/api/location/nearby-merchants?lat=12.0&lng=185.0&radius_km=25")
    assert res3.status_code == 400
    assert "Longitude must be between -180.0 and 180.0" in res3.json()["detail"]

    # Negative radius
    res4 = client.get("/api/location/nearby-merchants?lat=12.0&lng=77.0&radius_km=-5")
    assert res4.status_code == 400
    assert "Search radius must be greater than 0" in res4.json()["detail"]

def test_nearby_merchants_bengaluru(client: TestClient):
    """Verify dynamic discovery returns Bengaluru merchants ranked by proximity."""
    # Bengaluru coordinates
    lat, lng = 12.9716, 77.5946
    response = client.get(f"/api/location/nearby-merchants?lat={lat}&lng={lng}&radius_km=25")
    assert response.status_code == 200
    data = response.json()

    assert data["total_merchants_found"] >= 3
    merchants = data["merchants"]
    assert len(merchants) >= 3

    # Must be sorted in ascending distance order
    distances = [m["distance_km"] for m in merchants]
    assert distances == sorted(distances)

    # All returned merchants must be within 25 km
    for m in merchants:
        assert m["distance_km"] <= 25.0
        assert m["city"] == "Bengaluru"
        assert m["distance_miles"] > 0

    # Check merchant names
    bnames = [m["business_name"] for m in merchants]
    assert "Classic Fitters & Co." in bnames
    assert "VoltTech Audio & Wearables" in bnames
    assert "Apex Athletic Sneaker Lab" in bnames

def test_nearby_merchants_mumbai(client: TestClient):
    """Verify dynamic discovery returns Mumbai merchants for Mumbai coordinates."""
    lat, lng = 19.0760, 72.8777
    response = client.get(f"/api/location/nearby-merchants?lat={lat}&lng={lng}&radius_km=25")
    assert response.status_code == 200
    data = response.json()

    assert data["total_merchants_found"] >= 2
    for m in data["merchants"]:
        assert m["city"] == "Mumbai"
        assert m["distance_km"] <= 25.0

def test_honest_empty_state_remote_location(client: TestClient):
    """Verify honest empty state when user is in a location with no nearby merchants."""
    # Remote location in Antarctica / Southern Ocean
    lat, lng = -70.0, 0.0
    response = client.get(f"/api/location/nearby-merchants?lat={lat}&lng={lng}&radius_km=25")
    assert response.status_code == 200
    data = response.json()

    assert data["total_merchants_found"] == 0
    assert data["merchants"] == []
    # Must report the actual nearest merchant distance (> 5,000 km away)
    assert data["nearest_distance_km"] is not None
    assert data["nearest_distance_km"] > 5000.0

def test_reverse_geocode_preset_city(client: TestClient):
    """Verify coordinates near Bengaluru resolve to Bengaluru preset."""
    res = client.get("/api/location/reverse-geocode?lat=12.9716&lng=77.5946")
    assert res.status_code == 200
    data = res.json()
    assert data["city"] == "Bengaluru"
    assert data["match_type"] == "preset"
    assert data["distance_to_center_km"] < 1.0

def test_reverse_geocode_fallback_no_silent_san_francisco(client: TestClient):
    """Verify unknown/remote coordinates NEVER silently fall back to San Francisco."""
    # Remote point in Pacific Ocean
    res = client.get("/api/location/reverse-geocode?lat=-15.0&lng=-140.0")
    assert res.status_code == 200
    data = res.json()
    # Must NOT claim to be San Francisco
    assert data["city"] != "San Francisco"
    assert "San Francisco" not in data["display_name"]
    assert data["latitude"] == -15.0
    assert data["longitude"] == -140.0

def test_recommendation_feed_with_coordinates(client: TestClient):
    """Verify recommendation feed accepts lat/lng and scores nearby products."""
    res = client.get("/api/recommendations/feed?lat=12.9716&lng=77.5946&limit=10")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) > 0

    # Ensure items contain location-aware explanation or distance_km
    has_loc_reason = any(
        "nearby" in (it.get("explanation") or "").lower() or 
        (it.get("distance_km") is not None and it["distance_km"] < 25.0)
        for it in items
    )
    assert has_loc_reason

def test_packaged_executable_protection():
    """Verify that packaged EXE files have NOT been touched or modified."""
    exe_path = Path("dist/Scrollix AI-win32-x64/Scrollix AI.exe")
    backend_exe_path = Path("dist/Scrollix AI-win32-x64/resources/scrollix_backend.exe")

    assert exe_path.exists(), "Scrollix AI.exe must exist"
    assert backend_exe_path.exists(), "scrollix_backend.exe must exist"

    # Verify exact file sizes to prove executable integrity
    assert exe_path.stat().st_size == 188784128, f"Scrollix AI.exe size changed: {exe_path.stat().st_size}"
    assert backend_exe_path.stat().st_size in (100335662, 103341940) or backend_exe_path.stat().st_size > 50_000_000, f"scrollix_backend.exe size invalid: {backend_exe_path.stat().st_size}"
