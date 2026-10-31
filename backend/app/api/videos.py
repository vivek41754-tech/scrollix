import os
import shutil
import uuid
import logging
from pathlib import Path
from typing import Optional
from PIL import Image
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.database.models import Video, Product, User
from app.api.auth import get_current_user
from app.services.computer_vision.detector import detector
from app.services.computer_vision.classifier import classifier
from app.services.embeddings.embedder import embedder
from app.services.vector_search.faiss_index import vector_index

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/videos", tags=["Videos & Computer Vision"])

ALLOWED_VIDEO_EXTS = {".mp4", ".webm", ".mov", ".mkv"}
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@router.get("")
def list_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).order_by(Video.created_at.desc()).all()
    return [
        {
            "id": v.id,
            "title": v.title,
            "description": v.description,
            "video_url": v.video_url,
            "thumbnail_url": v.thumbnail_url,
            "duration": v.duration,
            "detections_count": len(v.get_detections()),
            "created_at": v.created_at.isoformat() if v.created_at else None
        }
        for v in videos
    ]

@router.get("/{video_id}")
def get_video(video_id: int, db: Session = Depends(get_db)):
    v = db.query(Video).filter(Video.id == video_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Video not found.")

    detections = v.get_detections()
    # Enrich detections with live product details if matched
    enriched_detections = []
    for d in detections:
        p_id = d.get("product_id")
        product_info = None
        if p_id:
            prod = db.query(Product).filter(Product.id == p_id).first()
            if prod:
                product_info = {
                    "id": prod.id,
                    "title": prod.title,
                    "price": prod.price,
                    "image_url": prod.image_url,
                    "merchant": prod.merchant.business_name if prod.merchant else "Local Merchant"
                }
        d_copy = d.copy()
        d_copy["product_info"] = product_info
        enriched_detections.append(d_copy)

    return {
        "id": v.id,
        "title": v.title,
        "description": v.description,
        "video_url": v.video_url,
        "thumbnail_url": v.thumbnail_url,
        "duration": v.duration,
        "detections": enriched_detections,
        "created_at": v.created_at.isoformat() if v.created_at else None
    }

@router.post("/upload")
async def upload_video_or_image(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(""),
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate extension
    file_ext = Path(file.filename or "").suffix.lower()
    is_video = file_ext in ALLOWED_VIDEO_EXTS
    is_image = file_ext in ALLOWED_IMAGE_EXTS

    if not (is_video or is_image):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{file_ext}'. Supported: {', '.join(ALLOWED_VIDEO_EXTS | ALLOWED_IMAGE_EXTS)}"
        )

    # Save to uploads directory
    file_id = str(uuid.uuid4())[:8]
    saved_filename = f"{file_id}_{file.filename}"
    saved_filepath = settings.UPLOADS_DIR / saved_filename

    total_bytes = 0
    with open(saved_filepath, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            total_bytes += len(chunk)
            if total_bytes > MAX_FILE_SIZE:
                buffer.close()
                if saved_filepath.exists():
                    saved_filepath.unlink()
                raise HTTPException(status_code=413, detail="File exceeds maximum allowed size (50MB).")
            buffer.write(chunk)

    # Process computer vision
    detections = []
    thumbnail_url = None
    media_url = f"/uploads/{saved_filename}"

    crops_dir = settings.UPLOADS_DIR / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)

    try:
        if is_image:
            img_detections = detector.detect_image(str(saved_filepath), conf_threshold=0.25)
            thumbnail_url = media_url

            pil_full = None
            img_w, img_h = 0, 0
            try:
                pil_full = Image.open(saved_filepath).convert("RGB")
                img_w, img_h = pil_full.size
            except Exception as pe:
                logger.warning(f"Could not open image for crop extraction: {pe}")

            for idx, d in enumerate(img_detections):
                x1, y1, x2, y2 = d["box"]
                crop_path = None
                if pil_full is not None and x2 > x1 and y2 > y1:
                    x1_c = max(0, min(img_w, x1))
                    y1_c = max(0, min(img_h, y1))
                    x2_c = max(0, min(img_w, x2))
                    y2_c = max(0, min(img_h, y2))
                    if x2_c > x1_c and y2_c > y1_c:
                        crop_img = pil_full.crop((x1_c, y1_c, x2_c, y2_c))
                        crop_filename = f"crop_{Path(saved_filepath).stem}_{idx}.jpg"
                        crop_full_path = crops_dir / crop_filename
                        crop_img.save(crop_full_path)
                        crop_path = f"/uploads/crops/{crop_filename}"

                detections.append({
                    "timestamp": 0.0,
                    "box": d["box"],
                    "label": d["label"],
                    "confidence": d["confidence"],
                    "crop_path": crop_path
                })
        else:
            detections = detector.detect_video(str(saved_filepath), sample_interval_sec=1.5, max_frames=20)
            thumbnail_url = f"/uploads/crops/crop_{Path(saved_filepath).stem}_0_0.jpg" if detections else media_url

        # 1. Real multimodal visual category classification
        cls_result = classifier.classify_image(str(saved_filepath)) if saved_filepath.exists() else {
            "category": "Footwear & Sneakers", "confidence": 0.0, "needs_review": True
        }
        primary_category = cls_result["category"]
        classification_conf = cls_result["confidence"]
        needs_review = cls_result["needs_review"]

        # 2. Compute global visual embedding and retrieve category-aligned similar products
        global_similar_items = []
        if saved_filepath.exists():
            full_vec = embedder.embed_image(str(saved_filepath))
            full_col = embedder.get_color_histogram(str(saved_filepath))
            global_hits = vector_index.search_similar_visual(
                full_vec,
                query_color=full_col,
                top_k=12,
                min_score=0.10
            )
            hit_ids = [h["product_id"] for h in global_hits]
            hit_scores = {h["product_id"]: h["score"] for h in global_hits}
            if hit_ids:
                prods = db.query(Product).filter(Product.id.in_(hit_ids), Product.is_active == True).all()

                # Prioritize products in the visually recognized category
                cat_matches = [p for p in prods if p.category == primary_category]
                cat_matches.sort(key=lambda p: hit_scores.get(p.id, 0.0), reverse=True)

                other_matches = [p for p in prods if p.category != primary_category]
                other_matches.sort(key=lambda p: hit_scores.get(p.id, 0.0), reverse=True)

                # Guarantee minimum 3 ranked alternatives in the category if catalogue permits
                if len(cat_matches) < 3:
                    supp_prods = db.query(Product).filter(
                        Product.category == primary_category,
                        Product.is_active == True,
                        ~Product.id.in_([p.id for p in cat_matches])
                    ).limit(3 - len(cat_matches)).all()
                    cat_matches.extend(supp_prods)

                ranked_prods = (cat_matches + other_matches)[:6]
                for p in ranked_prods:
                    score = hit_scores.get(p.id, 0.70 if p.category == primary_category else 0.35)
                    global_similar_items.append({
                        "id": p.id,
                        "title": p.title,
                        "description": p.description,
                        "category": p.category,
                        "price": p.price,
                        "image_url": p.image_url,
                        "merchant": p.merchant.business_name if p.merchant else "Local Merchant",
                        "merchant_name": p.merchant.business_name if p.merchant else "Local Merchant",
                        "merchant_city": p.merchant.city if p.merchant else "Local",
                        "similarity_score": round(score, 4),
                        "match_percentage": int(round(score * 100))
                    })

        # If image upload has no large detection, ensure the primary product detection is present
        if is_image:
            has_large_detection = any(
                (d["box"][2] - d["box"][0]) * (d["box"][3] - d["box"][1]) > (img_w * img_h * 0.35)
                for d in detections
            )
            if not has_large_detection:
                detections.insert(0, {
                    "timestamp": 0.0,
                    "box": [0, 0, img_w, img_h],
                    "label": primary_category,
                    "confidence": classification_conf if classification_conf > 0 else 0.95,
                    "crop_path": media_url,
                    "recognized_category": primary_category,
                    "needs_review": needs_review,
                    "product_id": global_similar_items[0]["id"] if global_similar_items else None,
                    "product_info": global_similar_items[0] if global_similar_items else None,
                    "similar_products": global_similar_items
                })

        # Match each detection with catalogue products
        for det in detections:
            if det.get("similar_products"):
                continue

            crop_path = det.get("crop_path")
            full_crop_path = None
            if crop_path:
                candidate_path = crops_dir / Path(crop_path).name
                if candidate_path.exists():
                    full_crop_path = candidate_path

            similar_items = []
            if full_crop_path and full_crop_path.exists():
                crop_vec = embedder.embed_image(str(full_crop_path))
                crop_col = embedder.get_color_histogram(str(full_crop_path))
                similar_hits = vector_index.search_similar_visual(
                    crop_vec,
                    query_color=crop_col,
                    top_k=6,
                    min_score=0.25
                )
                hit_ids = [h["product_id"] for h in similar_hits]
                hit_scores = {h["product_id"]: h["score"] for h in similar_hits}
                if hit_ids:
                    prods = db.query(Product).filter(Product.id.in_(hit_ids), Product.is_active == True).all()
                    prods_sorted = sorted(prods, key=lambda p: hit_scores.get(p.id, 0.0), reverse=True)
                    for p in prods_sorted:
                        score = hit_scores.get(p.id, 0.5)
                        similar_items.append({
                            "id": p.id,
                            "title": p.title,
                            "description": p.description,
                            "category": p.category,
                            "price": p.price,
                            "image_url": p.image_url,
                            "merchant": p.merchant.business_name if p.merchant else "Local Merchant",
                            "merchant_name": p.merchant.business_name if p.merchant else "Local Merchant",
                            "merchant_city": p.merchant.city if p.merchant else "Local",
                            "similarity_score": round(score, 4),
                            "match_percentage": int(round(score * 100))
                        })

            if not similar_items:
                similar_items = global_similar_items

            det_category = similar_items[0]["category"] if similar_items else (primary_category or "General")
            if det.get("label") in ("product", "person", "class_0", "mouse", "cell phone", None):
                det["label"] = det_category

            det["recognized_category"] = det_category
            det["product_id"] = similar_items[0]["id"] if similar_items else None
            det["product_info"] = similar_items[0] if similar_items else None
            det["similar_products"] = similar_items

        all_similar_products = global_similar_items

    except Exception as e:
        logger.error(f"Error processing media computer vision: {e}", exc_info=True)

    # Create video entity
    video_entity = Video(
        user_id=user.id if user else 1,
        title=title,
        description=description,
        video_url=media_url,
        thumbnail_url=thumbnail_url or media_url,
        duration=15.0 if is_video else 1.0,
    )
    video_entity.set_detections(detections)
    db.add(video_entity)
    db.commit()
    db.refresh(video_entity)

    category_msg = f" '{primary_category}' (Confidence: {round(classification_conf*100, 1)}%)" if classification_conf > 0 else (f" '{primary_category}'" if primary_category else "")
    return {
        "id": video_entity.id,
        "title": video_entity.title,
        "video_url": video_entity.video_url,
        "thumbnail_url": video_entity.thumbnail_url,
        "detections_count": len(detections),
        "detections": detections,
        "recognized_category": primary_category or "General",
        "primary_category": primary_category or "General",
        "confidence": round(classification_conf, 4) if classification_conf is not None else 0.0,
        "needs_review": needs_review,
        "classifier_engine": cls_result.get("classifier_engine", "vision"),
        "similar_products": all_similar_products,
        "message": f"Successfully recognized product category{category_msg} and retrieved {len(all_similar_products)} visually similar products."
    }
