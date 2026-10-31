from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import FraudFlag, Merchant, User
from app.api.auth import require_role
from app.services.fraud.detector import fraud_detector

router = APIRouter(prefix="/fraud", tags=["Fraud Detection & Trust Scoring"])

class ResolveFlagRequest(BaseModel):
    action: str  # approved, dismissed
    note: Optional[str] = ""

@router.get("/flags")
def list_fraud_flags(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(FraudFlag)
    if status:
        query = query.filter(FraudFlag.status == status)
    
    flags = query.order_by(FraudFlag.flagged_at.desc()).all()
    results = []
    for f in flags:
        target_name = "Unknown Target"
        if f.target_type == "merchant":
            m = db.query(Merchant).filter(Merchant.id == f.target_id).first()
            if m:
                target_name = m.business_name

        results.append({
            "id": f.id,
            "target_type": f.target_type,
            "target_id": f.target_id,
            "target_name": target_name,
            "risk_score": f.risk_score,
            "reasons": f.get_reasons(),
            "status": f.status,
            "flagged_at": f.flagged_at.isoformat() if f.flagged_at else None,
            "resolved_at": f.resolved_at.isoformat() if f.resolved_at else None
        })
    return results

@router.post("/scan")
def run_fraud_scan(db: Session = Depends(get_db)):
    """Triggers explainable fraud scan across all merchants."""
    results = fraud_detector.scan_all_merchants(db)
    return {
        "scanned_merchants_count": len(results),
        "results": results
    }

@router.post("/flags/{flag_id}/resolve")
def resolve_flag(flag_id: int, req: ResolveFlagRequest, user: User = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    flag = db.query(FraudFlag).filter(FraudFlag.id == flag_id).first()
    if not flag:
        raise HTTPException(status_code=404, detail="Fraud flag not found.")

    if req.action not in ["approved", "dismissed"]:
        raise HTTPException(status_code=400, detail="Action must be 'approved' or 'dismissed'.")

    flag.status = req.action
    flag.resolved_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "id": flag.id,
        "status": flag.status,
        "resolved_at": flag.resolved_at.isoformat(),
        "message": f"Flag {req.action} successfully by administrator."
    }
