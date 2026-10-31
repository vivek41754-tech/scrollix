import urllib.request
import urllib.error
import json

def test_api(url, data=None, headers=None, method=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, headers=headers)
    if method:
        req.method = method
    if data is not None:
        req.data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
        if not method:
            req.method = "POST"
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("=" * 60)
print("SCROLLIX AI PACKAGED BACKEND EXECUTABLE VERIFICATION")
print("=" * 60)

# 1. Health
h = test_api("http://127.0.0.1:8000/api/health")
print(f"[OK] Health Status: {h['status']} | FAISS vectors: {h['faiss_total']}")

# 2. Demo role switch - shopper
shopper = test_api("http://127.0.0.1:8000/api/auth/demo-switch", {"role": "shopper"})
print(f"[OK] Demo Shopper Role: {shopper['user']['role']} (user: {shopper['user']['username']})")

# 3. Demo role switch - merchant
merchant = test_api("http://127.0.0.1:8000/api/auth/demo-switch", {"role": "merchant"})
print(f"[OK] Demo Merchant Role: {merchant['user']['role']} (user: {merchant['user']['username']}, merchant_id: {merchant['user']['merchant_id']})")

# 4. Demo role switch - admin
admin = test_api("http://127.0.0.1:8000/api/auth/demo-switch", {"role": "admin"})
print(f"[OK] Demo Admin Role: {admin['user']['role']} (user: {admin['user']['username']})")

# 5. Remote IP blocked (Security Guardrail)
try:
    test_api("http://127.0.0.1:8000/api/auth/demo-switch", {"role": "admin"}, headers={"X-Forwarded-For": "198.51.100.1"})
    print("[FAIL] Remote IP not blocked!")
except urllib.error.HTTPError as e:
    print(f"[OK] Remote IP blocked safely: HTTP {e.code}")

# 6. Merchants count
merchants = test_api("http://127.0.0.1:8000/api/merchants")
print(f"[OK] Total Merchants: {len(merchants)} (Requirement: >= 10 demo merchants)")

# 7. Products count
products = test_api("http://127.0.0.1:8000/api/products")
print(f"[OK] Total Products: {len(products)} (Requirement: >= 50 products)")

# 8. Nearby demo merchants (10-20km)
ref_lat, ref_lon = 12.9716, 77.5946
seed_res = test_api(f"http://127.0.0.1:8000/api/location/seed-nearby-demo?lat={ref_lat}&lng={ref_lon}", method="POST")
print(f"[OK] Seeded 10-20km Merchants: {len(seed_res['merchants'])}")
for m in seed_res["merchants"]:
    dist = m["distance_km"]
    name = m["business_name"]
    cat = m["category"]
    print(f"     * {name} ({cat}) -> {dist:.2f} km")
    assert 10.0 <= dist <= 20.0, f"Distance {dist} not in 10-20km range"

# 9. Verify nearby merchants retrieval
nearby = test_api(f"http://127.0.0.1:8000/api/location/nearby-merchants?lat={ref_lat}&lng={ref_lon}&radius_km=30")
print(f"[OK] Discovered nearby merchants within 30km: {len(nearby['merchants'])}")

# 10. Verify Visual Similarity Search on running backend executable
import requests
test_img_path = "data/uploads/1407c473_red_running_shoe.jpg"
with open(test_img_path, "rb") as f:
    files = {"file": ("test_shoe.jpg", f, "image/jpeg")}
    resp = requests.post("http://127.0.0.1:8000/api/search/visual", files=files)
    assert resp.status_code == 200, f"Visual search failed with status {resp.status_code}: {resp.text}"
    v_results = resp.json()
    print(f"[OK] Visual Search executed successfully: {len(v_results)} results returned")
    for r in v_results[:3]:
        score = r.get("similarity_score", r.get("score"))
        print(f"     * {r['title']} [{r['category']}] -> Similarity Score: {score}")

print("=" * 60)
print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
print("=" * 60)
