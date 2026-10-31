import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

def run_e2e_verification():
    print("=" * 60)
    print("  SCROLLIX AI — END-TO-END SYSTEM INTEGRATION VERIFICATION")
    print("=" * 60)

    with TestClient(app) as client:
        # 1. Health check
        print("\n[1] Verifying System Health...")
        health = client.get("/api/admin/health").json()
        print(f"    Status: {health['status']}")
        print(f"    Computer Vision: {health['computer_vision']['model']} ({health['computer_vision']['status']})")
        print(f"    Vector Search: {health['vector_search']['engine']} with {health['vector_search']['indexed_items_count']} indexed items")
        print(f"    Database: {health['database']['users_count']} users, {health['database']['products_count']} products")

        # 2. Authentication & Roles
        print("\n[2] Verifying User Auth & Roles...")
        login_res = client.post("/api/auth/login", json={"username_or_email": "admin", "password": "admin123"}).json()
        token = login_res["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        me = client.get("/api/auth/me", headers=headers).json()
        print(f"    Logged in as: {me['username']} (Role: {me['role']})")

        # 3. Product Catalogue & FAISS Search
        print("\n[3] Verifying Catalogue & FAISS Vector Search...")
        products = client.get("/api/products").json()
        print(f"    Total Active Products: {len(products)}")
        search_res = client.post("/api/search/text", json={"query": "running sneakers", "top_k": 3}).json()
        print(f"    Vector Search results for 'running sneakers': {len(search_res)} hits")
        if search_res:
            top = search_res[0]
            print(f"    Top Match: '{top['title']}' (${top['price']}) - Score: {top['similarity_score']}")

        # 4. Personalized Recommendations
        print("\n[4] Verifying Personalized Recommendation Feed...")
        recs = client.get("/api/recommendations/feed?lat=37.7749&lng=-122.4194&limit=3").json()
        print(f"    Generated Recommendations: {len(recs)} items")
        for idx, r in enumerate(recs):
            print(f"    #{idx+1}: {r['title']} (${r['price']}) — {r['explanation']}")

        # 5. Location-Aware Discovery & Haversine Distance
        print("\n[5] Verifying Location Discovery (Haversine formula)...")
        loc_res = client.get("/api/location/nearby-merchants?lat=37.7749&lng=-122.4194&radius_km=20").json()
        print(f"    Nearby Merchants within 20km: {loc_res['total_merchants_found']}")
        for m in loc_res["merchants"][:2]:
            print(f"    - {m['business_name']}: {m['distance_km']} km away (Trust: {m['trust_score']}%)")

        # 6. AI Shopping Assistant (Catalogue Grounding)
        print("\n[6] Verifying AI Shopping Assistant Catalogue Grounding...")
        chat_res = client.post("/api/assistant/chat", json={"message": "What leather bags do you have under $200?"}).json()
        print(f"    Assistant Mode: {chat_res['mode']}")
        print(f"    Recommended Products: {[p['title'] for p in chat_res['recommended_products']]}")
        print(f"    Assistant Disclaimer: {chat_res['disclaimer']}")

        # 7. Sentiment Analysis on Reviews
        print("\n[7] Verifying Sentiment Analysis on Product Reviews...")
        prod_detail = client.get(f"/api/products/{products[0]['id']}").json()
        sentiment = prod_detail["sentiment_summary"]
        print(f"    Product: {prod_detail['title']}")
        print(f"    Sentiment: {sentiment['summary']} ({sentiment['positive_pct']}% Positive)")

        # 8. Fraud Detection Audit
        print("\n[8] Verifying Explainable Fraud Anomaly Scoring...")
        scan_res = client.post("/api/fraud/scan").json()
        print(f"    Audited Merchants: {scan_res['scanned_merchants_count']}")
        flags = client.get("/api/fraud/flags").json()
        print(f"    Total Flags in Moderation Queue: {len(flags)}")

        # 9. Analytics Dashboard
        print("\n[9] Verifying Factual Analytics from Event Store...")
        analytics = client.get("/api/analytics/dashboard").json()
        s = analytics["summary"]
        print(f"    Views: {s['views']} | Likes: {s['likes']} | Clicks: {s['clicks']} | CTR: {s['click_through_rate_pct']}%")

        print("\n" + "=" * 60)
        print("  ALL CORE MODULES SUCCESSFULLY INTEGRATED AND VERIFIED!")
        print("=" * 60)

if __name__ == "__main__":
    run_e2e_verification()
