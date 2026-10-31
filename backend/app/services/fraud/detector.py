import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import Merchant, Product, User, Review, FraudFlag

logger = logging.getLogger(__name__)

class FraudDetector:
    def __init__(self):
        self.suspicious_threshold = 40.0  # Risk score >= 40 triggers admin review flag

    def evaluate_merchant(self, db: Session, merchant_id: int) -> dict:
        """
        Evaluates a merchant profile and recent product listings for suspicious anomalies.
        Returns explainable signals and risk score.
        """
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            return {"risk_score": 0.0, "is_suspicious": False, "reasons": ["Merchant not found"]}

        products = db.query(Product).filter(Product.merchant_id == merchant_id).all()
        risk_score = 0.0
        reasons = []

        # Signal 1: Incomplete or suspicious merchant profile
        if not merchant.phone or len(merchant.phone.strip()) < 7:
            risk_score += 15.0
            reasons.append("Unverified contact number or missing merchant phone.")

        if not merchant.address or len(merchant.address.strip()) < 5:
            risk_score += 15.0
            reasons.append("Missing physical storefront/warehouse address.")

        # Signal 2: Rapid listing velocity
        five_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        recent_listings = [p for p in products if p.created_at and p.created_at.replace(tzinfo=timezone.utc) >= five_mins_ago]
        if len(recent_listings) >= 8:
            risk_score += 35.0
            reasons.append(f"Abnormal listing velocity: Created {len(recent_listings)} products within 5 minutes.")

        # Signal 3: Duplicate or near-duplicate product titles
        titles = [p.title.lower().strip() for p in products]
        duplicate_count = len(titles) - len(set(titles))
        if duplicate_count > 0:
            dup_penalty = min(30.0, duplicate_count * 10.0)
            risk_score += dup_penalty
            reasons.append(f"Detected {duplicate_count} duplicate product listing(s) across catalog.")

        # Signal 4: Extreme price outliers
        for p in products:
            if p.price <= 0.01:
                risk_score += 25.0
                reasons.append(f"Suspicious pricing ($0.01 or less) detected on product: '{p.title}'.")
                break
            elif p.price >= 5000.0:
                risk_score += 20.0
                reasons.append(f"High-value luxury price (${p.price:,.2f}) listed by unverified account: '{p.title}'.")
                break

        # Adjust score if merchant is already verified with good history
        if merchant.is_verified:
            risk_score = max(0.0, risk_score - 25.0)

        risk_score = min(100.0, round(risk_score, 1))
        is_suspicious = risk_score >= self.suspicious_threshold

        # Update merchant trust score
        new_trust_score = max(10.0, min(100.0, 100.0 - risk_score))
        merchant.trust_score = round(new_trust_score, 1)

        # Record or update fraud flag for admin review
        if is_suspicious:
            existing_flag = db.query(FraudFlag).filter(
                FraudFlag.target_type == "merchant",
                FraudFlag.target_id == merchant_id,
                FraudFlag.status == "pending"
            ).first()

            if not existing_flag:
                new_flag = FraudFlag(
                    target_type="merchant",
                    target_id=merchant_id,
                    risk_score=risk_score,
                    status="pending"
                )
                new_flag.set_reasons(reasons)
                db.add(new_flag)
            else:
                existing_flag.risk_score = risk_score
                existing_flag.set_reasons(reasons)

        db.commit()

        return {
            "merchant_id": merchant_id,
            "business_name": merchant.business_name,
            "risk_score": risk_score,
            "trust_score": merchant.trust_score,
            "is_suspicious": is_suspicious,
            "reasons": reasons if reasons else ["Merchant profile and listing patterns within normal parameters."]
        }

    def scan_all_merchants(self, db: Session) -> list[dict]:
        """Runs audit across all active merchants."""
        merchants = db.query(Merchant).all()
        results = []
        for m in merchants:
            res = self.evaluate_merchant(db, m.id)
            results.append(res)
        return results

fraud_detector = FraudDetector()
