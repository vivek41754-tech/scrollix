import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import Interaction, Product, Merchant, Video, Review

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    def get_dashboard_metrics(self, db: Session, merchant_id: Optional[int] = None) -> dict:
        """
        Calculates factual business and engagement metrics strictly from persisted database events.
        """
        # Base queries
        interaction_q = db.query(Interaction)
        product_q = db.query(Product).filter(Product.is_active == True)

        if merchant_id:
            # Filter to products owned by merchant
            merchant_prod_ids = [p.id for p in db.query(Product.id).filter(Product.merchant_id == merchant_id).all()]
            interaction_q = interaction_q.filter(Interaction.product_id.in_(merchant_prod_ids))
            product_q = product_q.filter(Product.merchant_id == merchant_id)

        all_interactions = interaction_q.all()

        total_interactions = len(all_interactions)
        views = sum(1 for it in all_interactions if it.interaction_type == "view")
        likes = sum(1 for it in all_interactions if it.interaction_type == "like")
        clicks = sum(1 for it in all_interactions if it.interaction_type == "click")
        purchases = sum(1 for it in all_interactions if it.interaction_type == "purchase_intent")

        # Ratios
        ctr = round((clicks / views * 100), 2) if views > 0 else 0.0
        conversion_rate = round((purchases / clicks * 100), 2) if clicks > 0 else 0.0
        avg_dwell_time = round(sum(it.dwell_time for it in all_interactions) / max(1, views), 1)

        # Time-series (last 7 days)
        now = datetime.now(timezone.utc)
        time_series = []
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            day_label = day_start.strftime("%b %d")

            day_views = sum(1 for it in all_interactions if it.interaction_type == "view" and day_start <= it.created_at.replace(tzinfo=timezone.utc) < day_end)
            day_likes = sum(1 for it in all_interactions if it.interaction_type == "like" and day_start <= it.created_at.replace(tzinfo=timezone.utc) < day_end)
            day_clicks = sum(1 for it in all_interactions if it.interaction_type == "click" and day_start <= it.created_at.replace(tzinfo=timezone.utc) < day_end)

            time_series.append({
                "date": day_label,
                "views": day_views,
                "likes": day_likes,
                "clicks": day_clicks
            })

        # Top products by engagement
        product_engagements = {}
        for it in all_interactions:
            if it.product_id:
                product_engagements[it.product_id] = product_engagements.get(it.product_id, 0) + 1

        sorted_pids = sorted(product_engagements.items(), key=lambda x: x[1], reverse=True)[:5]
        top_products = []
        for pid, count in sorted_pids:
            p = db.query(Product).filter(Product.id == pid).first()
            if p:
                top_products.append({
                    "id": p.id,
                    "title": p.title,
                    "category": p.category,
                    "price": p.price,
                    "interactions_count": count
                })

        # Total counts in system
        total_products_count = product_q.count()
        total_merchants_count = db.query(Merchant).count()
        total_videos_count = db.query(Video).count()
        total_reviews_count = db.query(Review).count()

        return {
            "summary": {
                "total_interactions": total_interactions,
                "views": views,
                "likes": likes,
                "clicks": clicks,
                "purchases": purchases,
                "click_through_rate_pct": ctr,
                "conversion_rate_pct": conversion_rate,
                "average_dwell_time_sec": avg_dwell_time,
                "total_products": total_products_count,
                "total_merchants": total_merchants_count,
                "total_videos": total_videos_count,
                "total_reviews": total_reviews_count
            },
            "time_series": time_series,
            "top_products": top_products
        }

analytics_engine = AnalyticsEngine()
