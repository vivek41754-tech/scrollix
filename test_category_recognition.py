import sys
sys.path.insert(0, "backend")
from fastapi.testclient import TestClient
from app.main import app

tc = TestClient(app)

test_images = [
    "3ed8c488_shoe.jpg",
    "06567380_white_sneakers.jpg",
    "1407c473_red_running_shoe.jpg",
    "31227119_casual_shirt.jpg",
    "2f499e87_headphones.jpg"
]

for img_name in test_images:
    p = f"data/uploads/{img_name}"
    with open(p, "rb") as f:
        res = tc.post("/api/videos/upload", files={"file": (img_name, f, "image/jpeg")}, data={"title": "Test", "description": "Testing"})
        data = res.json()
        cat = data.get("recognized_category")
        dets = [(d["label"], d.get("recognized_category")) for d in data.get("detections", [])]
        similar = [(p["title"], p["category"]) for p in data.get("similar_products", [])[:2]]
        print(f"File: {img_name} -> Category: {cat}")
        print(f"  Detections: {dets}")
        print(f"  Top Similar: {similar}")
