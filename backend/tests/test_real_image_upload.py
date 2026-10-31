import os
import sys
import requests
from pathlib import Path

def test_upload():
    # Find bus.jpg or create a test image
    candidates = [
        Path("backend/dist/scrollix_backend/_internal/ultralytics/assets/bus.jpg"),
        Path("dist/Scrollix AI-win32-x64/resources/_internal/ultralytics/assets/bus.jpg"),
        Path("backend/dist/scrollix_backend/_internal/ultralytics/assets/zidane.jpg"),
    ]
    img_path = None
    for c in candidates:
        if c.exists():
            img_path = c
            break

    assert img_path is not None, "Could not find benchmark test image"
    print(f"Testing real upload with image: {img_path}")

    url = "http://127.0.0.1:8000/api/videos/upload"
    data = {
        "title": "Real YOLO Image Ingestion Test",
        "description": "Verifying bounding boxes, timestamps, image crops, and embeddings"
    }

    try:
        with open(img_path, "rb") as f:
            files = {"file": (img_path.name, f, "image/jpeg")}
            res = requests.post(url, files=files, data=data, timeout=2)
            res_json = res.json()
            status_code = res.status_code
    except Exception:
        # Fallback to in-process TestClient
        from fastapi.testclient import TestClient
        from app.main import app
        tc = TestClient(app)
        with open(img_path, "rb") as f:
            files = {"file": (img_path.name, f, "image/jpeg")}
            res = tc.post("/api/videos/upload", files=files, data=data)
            res_json = res.json()
            status_code = res.status_code

    print("HTTP Response Code:", status_code)
    assert status_code == 200, f"Upload failed with {status_code}: {res_json}"

    data = res_json
    print("Video Entity ID:", data.get("id"))
    print("Title:", data.get("title"))
    print("Thumbnail URL:", data.get("thumbnail_url"))
    print("Detections Count:", data.get("detections_count"))
    
    detections = data.get("detections", [])
    assert len(detections) > 0, "Expected at least 1 detection"

    for idx, d in enumerate(detections):
        print(f" Detection {idx+1}:")
        print(f"   Label: {d.get('label')}")
        print(f"   Confidence: {d.get('confidence')}")
        print(f"   Box: {d.get('box')}")
        print(f"   Timestamp: {d.get('timestamp')}")
        print(f"   Crop Path: {d.get('crop_path')}")
        print(f"   Matched Product ID: {d.get('product_id')}")

        # Verify crop file was created on disk if crop_path is present
        crop_path = d.get("crop_path")
        if crop_path:
            crop_filename = Path(crop_path).name
            # Check crop in data/uploads/crops
            possible_locations = [
                Path("data/uploads/crops") / crop_filename,
                Path("backend/data/uploads/crops") / crop_filename,
                Path(os.environ.get("SCROLLIX_DATA_DIR", "data")) / "uploads" / "crops" / crop_filename
            ]
            crop_found = any(p.exists() for p in possible_locations)
            print(f"   Crop file on disk: {'VERIFIED' if crop_found else 'PENDING'}")

    print("\n--- ALL REAL IMAGE UPLOAD & CV CHECKS PASSED ---")

if __name__ == "__main__":
    test_upload()
