import os
import shutil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.database.models import User, Merchant, Product, Video, FraudFlag
from app.api.auth import require_role
from app.services.computer_vision.detector import detector
from app.services.vector_search.faiss_index import vector_index
from app.services.chatbot.assistant import assistant

router = APIRouter(prefix="/admin", tags=["Administration & Health"])

class UpdateRoleRequest(BaseModel):
    role: str

@router.get("/health")
def get_system_health(db: Session = Depends(get_db)):
    """Comprehensive health check for local AI models, datastores, and filesystem."""
    # Check database
    db_ok = False
    try:
        user_count = db.query(User).count()
        db_ok = True
    except Exception:
        user_count = 0

    # Disk usage
    total, used, free = shutil.disk_usage(str(settings.DATA_DIR))
    free_gb = round(free / (1024**3), 2)

    return {
        "status": "healthy" if db_ok else "degraded",
        "database": {
            "status": "online" if db_ok else "offline",
            "type": "SQLite (Local Standalone)",
            "users_count": user_count,
            "merchants_count": db.query(Merchant).count(),
            "products_count": db.query(Product).count(),
            "videos_count": db.query(Video).count()
        },
        "computer_vision": {
            "model": "Ultralytics YOLOv11 Nano",
            "status": "online" if detector.is_available else "offline_fallback",
            "weights_path": str(settings.YOLO_MODEL_PATH),
            "file_exists": os.path.exists(settings.YOLO_MODEL_PATH)
        },
        "vector_search": {
            "engine": "FAISS (IndexFlatIP Cosine)",
            "status": "ready",
            "indexed_items_count": vector_index.index.ntotal,
            "vector_dimension": vector_index.dim
        },
        "ai_chatbot": {
            "gemini_api_configured": bool(assistant.api_key),
            "fallback_mode": "local_catalogue_assistant" if not assistant.api_key else "gemini_cloud_with_local_fallback"
        },
        "storage": {
            "data_directory": str(settings.DATA_DIR),
            "free_space_gb": free_gb
        }
    }

@router.get("/users")
def list_users(user: User = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]

@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, req: UpdateRoleRequest, admin: User = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    if req.role not in ["customer", "merchant", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role.")

    target_user.role = req.role
    db.commit()
    return {"message": f"Updated role of {target_user.username} to {req.role}."}
