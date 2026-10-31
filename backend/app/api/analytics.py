from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.analytics.engine import analytics_engine

router = APIRouter(prefix="/analytics", tags=["Analytics Dashboard"])

@router.get("/dashboard")
def get_analytics_dashboard(merchant_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    metrics = analytics_engine.get_dashboard_metrics(db, merchant_id=merchant_id)
    return metrics
