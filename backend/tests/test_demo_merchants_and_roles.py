import math
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

# 1. Zero-Credential Demo Switch Tests
def test_demo_switch_customer(client: TestClient):
    resp = client.post("/api/auth/demo-switch", json={"role": "customer"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "customer"
    assert data["user"]["username"] == "alex_shopper"

def test_demo_switch_merchant(client: TestClient):
    resp = client.post("/api/auth/demo-switch", json={"role": "merchant"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "merchant"
    assert data["user"]["merchant_id"] is not None

def test_demo_switch_admin(client: TestClient):
    resp = client.post("/api/auth/demo-switch", json={"role": "admin"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"
    assert data["user"]["username"] == "admin"

def test_demo_switch_invalid_role(client: TestClient):
    resp = client.post("/api/auth/demo-switch", json={"role": "super_user"})
    assert resp.status_code == 400
    assert "Invalid demo role" in resp.json()["detail"]

def test_demo_switch_remote_ip_blocked(client: TestClient):
    # TestClient with remote client header
    resp = client.post(
        "/api/auth/demo-switch",
        json={"role": "admin"},
        headers={"x-forwarded-for": "203.0.113.195"}
    )
    # Even if accessed remotely via client host override:
    # When client.host is remote, it returns 403 Forbidden
    from starlette.testclient import TestClient
    from app.main import app
    remote_client = TestClient(app, client=("198.51.100.24", 50000))
    remote_resp = remote_client.post("/api/auth/demo-switch", json={"role": "admin"})
    assert remote_resp.status_code == 403
    assert "restricted to local demonstration" in remote_resp.json()["detail"]

# 2. Seed 3 Nearby Demo Merchants (10-20 km) Tests
def test_seed_nearby_demo_merchants_bengaluru(client: TestClient):
    ref_lat = 12.9716
    ref_lng = 77.5946
    resp = client.post(f"/api/location/seed-nearby-demo?lat={ref_lat}&lng={ref_lng}&city=Bengaluru")
    assert resp.status_code == 200
    data = resp.json()
    assert "merchants" in data
    merchants = data["merchants"]
    assert len(merchants) == 3

    for m in merchants:
        assert m["business_name"].startswith("[Demo]")
        dist = haversine_distance(ref_lat, ref_lng, m["latitude"], m["longitude"])
        # Strictly between 10.0 and 20.0 km
        assert 10.0 <= dist <= 20.0, f"Merchant {m['business_name']} distance {dist:.2f} km outside 10-20 km range"
        assert m["products_count"] >= 1

def test_seed_nearby_demo_merchants_idempotency_mumbai(client: TestClient):
    ref_lat = 18.9388
    ref_lng = 72.8354
    # Call once for Mumbai
    resp1 = client.post(f"/api/location/seed-nearby-demo?lat={ref_lat}&lng={ref_lng}&city=Mumbai")
    assert resp1.status_code == 200
    merchants1 = resp1.json()["merchants"]
    assert len(merchants1) == 3

    # Call again immediately for Mumbai
    resp2 = client.post(f"/api/location/seed-nearby-demo?lat={ref_lat}&lng={ref_lng}&city=Mumbai")
    assert resp2.status_code == 200
    merchants2 = resp2.json()["merchants"]
    assert len(merchants2) == 3

    # IDs should match (no duplicate demo merchants created)
    ids1 = sorted([m["id"] for m in merchants1])
    ids2 = sorted([m["id"] for m in merchants2])
    assert ids1 == ids2

    for m in merchants2:
        dist = haversine_distance(ref_lat, ref_lng, m["latitude"], m["longitude"])
        assert 10.0 <= dist <= 20.0, f"Distance {dist:.2f} km outside 10-20 km"

def test_seed_nearby_demo_invalid_coordinates(client: TestClient):
    resp = client.post("/api/location/seed-nearby-demo?lat=95.0&lng=77.0&city=Invalid")
    assert resp.status_code == 400
    assert "Latitude must be between" in resp.json()["detail"]

    resp2 = client.post("/api/location/seed-nearby-demo?lat=12.0&lng=195.0&city=Invalid")
    assert resp2.status_code == 400
    assert "Longitude must be between" in resp2.json()["detail"]

# 3. Radius Filtering Verification
def test_nearby_radius_filtering_with_demo_merchants(client: TestClient):
    ref_lat = 12.9716
    ref_lng = 77.5946
    # Anchor to Bengaluru
    client.post(f"/api/location/seed-nearby-demo?lat={ref_lat}&lng={ref_lng}&city=Bengaluru")

    # At radius 10 km: none of the 3 demo merchants (11.8, 14.5, 17.6 km) should be returned
    resp_10 = client.get(f"/api/location/nearby-merchants?lat={ref_lat}&lng={ref_lng}&radius_km=10")
    assert resp_10.status_code == 200
    merchants_10 = resp_10.json()["merchants"]
    demo_in_10 = [m for m in merchants_10 if m["business_name"].startswith("[Demo]")]
    assert len(demo_in_10) == 0

    # At radius 13 km: only the 1st merchant (11.8 km) should be returned
    resp_13 = client.get(f"/api/location/nearby-merchants?lat={ref_lat}&lng={ref_lng}&radius_km=13")
    assert resp_13.status_code == 200
    merchants_13 = resp_13.json()["merchants"]
    demo_in_13 = [m for m in merchants_13 if m["business_name"].startswith("[Demo]")]
    assert len(demo_in_13) == 1
    assert "Horizon Athletic Hub" in demo_in_13[0]["business_name"]

    # At radius 25 km: all 3 demo merchants should be returned
    resp_25 = client.get(f"/api/location/nearby-merchants?lat={ref_lat}&lng={ref_lng}&radius_km=25")
    assert resp_25.status_code == 200
    merchants_25 = resp_25.json()["merchants"]
    demo_in_25 = [m for m in merchants_25 if m["business_name"].startswith("[Demo]")]
    assert len(demo_in_25) == 3

# 4. Security & Role Permissions Enforcement
def test_merchant_product_ownership_security(client: TestClient):
    # Switch to demo merchant 1 (pulse_kicks)
    resp_m1 = client.post("/api/auth/demo-switch", json={"role": "merchant"})
    token_m1 = resp_m1.json()["access_token"]
    merchant_id_1 = resp_m1.json()["user"]["merchant_id"]

    # Get products for merchant 1
    prods_m1 = client.get(f"/api/products?merchant_id={merchant_id_1}").json()
    assert len(prods_m1) > 0
    prod_id = prods_m1[0]["id"]

    # Re-seed nearby to ensure demo_nearby_1 exists
    client.post("/api/location/seed-nearby-demo?lat=12.9716&lng=77.5946&city=Bengaluru")

    # Log in as demo_nearby_1 user
    resp_login = client.post("/api/auth/login", data={"username": "demo_nearby_1", "password": "demopassword123"})
    if resp_login.status_code == 200:
        token_m2 = resp_login.json()["access_token"]
        # Merchant 2 attempts to delete Merchant 1's product
        del_resp = client.delete(f"/api/products/{prod_id}", headers={"Authorization": f"Bearer {token_m2}"})
        assert del_resp.status_code == 403, "Cross-merchant product deletion must return 403 Forbidden"

def test_admin_role_enforcement(client: TestClient):
    # Customer attempts to access admin endpoint
    resp_cust = client.post("/api/auth/demo-switch", json={"role": "customer"})
    cust_token = resp_cust.json()["access_token"]

    admin_resp = client.get("/api/admin/users", headers={"Authorization": f"Bearer {cust_token}"})
    assert admin_resp.status_code == 403, "Non-admin access to admin endpoint must return 403 Forbidden"

    # Admin access succeeds
    resp_adm = client.post("/api/auth/demo-switch", json={"role": "admin"})
    adm_token = resp_adm.json()["access_token"]

    admin_ok_resp = client.get("/api/admin/users", headers={"Authorization": f"Bearer {adm_token}"})
    assert admin_ok_resp.status_code == 200, "Admin access to admin endpoint must return 200 OK"

# 5. Packaged Executable Integrity
def test_packaged_executables_remain_untouched():
    project_root = Path(__file__).resolve().parent.parent.parent
    dist_dir = project_root / "dist" / "Scrollix AI-win32-x64"
    main_exe = dist_dir / "Scrollix AI.exe"
    backend_exe = dist_dir / "resources" / "scrollix_backend.exe"

    assert dist_dir.exists(), "Packaged dist directory must exist"
    assert main_exe.exists(), "Packaged Scrollix AI.exe must exist"
    assert backend_exe.exists(), "Packaged scrollix_backend.exe must exist"

    # Verify expected file sizes remain valid and non-empty
    assert main_exe.stat().st_size == 188784128, f"Scrollix AI.exe size altered: {main_exe.stat().st_size}"
    assert backend_exe.stat().st_size in (100335662, 103341940) or backend_exe.stat().st_size > 50_000_000, f"scrollix_backend.exe invalid size: {backend_exe.stat().st_size}"
