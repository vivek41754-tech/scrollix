import logging
import random
from datetime import datetime, timezone, timedelta
from typing import Optional
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.database.models import User, Product, Video, Interaction, Merchant
from app.services.vector_search.faiss_index import vector_index
from app.services.embeddings.embedder import embedder
from app.services.location.distance import haversine_distance_km

logger = logging.getLogger(__name__)

class HybridRecommender:
    def __init__(self):
        # Weights for the hybrid recommender
        self.w_content = 0.35
        self.w_popularity = 0.25
        self.w_collaborative = 0.20
        self.w_location = 0.15
        self.exploration_rate = 0.05
        self.repetition_penalty = 0.30

    def get_recommended_feed(
        self,
        db: Session,
        user_id: Optional[int] = None,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
        limit: int = 15
    ) -> list[dict]:
        """
        Generates personalized, location-aware hybrid recommendations with explainable reasons.
        """
        products = db.query(Product).filter(Product.is_active == True).all()
        if not products:
            return []

        # 1. Fetch user interaction history
        user_interactions: list[Interaction] = []
        user_viewed_ids = set()
        user_liked_ids = set()
        user_pref_categories = set()

        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                prefs = user.get_preferences()
                user_pref_categories = set(prefs.get("preferred_categories", []))

            # Fetch recent user interactions (last 7 days)
            recent_time = datetime.now(timezone.utc) - timedelta(days=7)
            user_interactions = db.query(Interaction).filter(
                Interaction.user_id == user_id,
                Interaction.created_at >= recent_time
            ).all()

            for it in user_interactions:
                if it.product_id:
                    if it.interaction_type == "view":
                        user_viewed_ids.add(it.product_id)
                    elif it.interaction_type in ("like", "purchase_intent"):
                        user_liked_ids.add(it.product_id)

        # 2. Build Global Popularity Scores from persisted interactions
        popularity_counts = (
            db.query(
                Interaction.product_id,
                func.sum(
                    case(
                        (Interaction.interaction_type == "purchase_intent", 5.0),
                        (Interaction.interaction_type == "like", 3.0),
                        (Interaction.interaction_type == "click", 2.0),
                        else_=1.0
                    )
                ).label("score")
            )
            .filter(Interaction.product_id != None)
            .group_by(Interaction.product_id)
            .all()
        )
        pop_dict = {pid: float(score) for pid, score in popularity_counts if pid}
        max_pop = max(pop_dict.values()) if pop_dict and max(pop_dict.values()) > 0 else 1.0

        # 3. Build User Embedding Centroid for Content-Based Filtering
        user_profile_vec = None
        liked_products = [p for p in products if p.id in user_liked_ids]
        if liked_products:
            # Average vector of liked products
            vecs = []
            for lp in liked_products:
                v = embedder.embed_text(f"{lp.title} {lp.category} {lp.description}")
                vecs.append(v)
            if vecs:
                user_profile_vec = np.mean(vecs, axis=0)
                norm = np.linalg.norm(user_profile_vec)
                if norm > 0:
                    user_profile_vec = user_profile_vec / norm

        # 4. Rank each product
        scored_candidates = []
        for p in products:
            # Content score
            content_score = 0.0
            content_reason = None
            if user_profile_vec is not None:
                p_vec = embedder.embed_text(f"{p.title} {p.category} {p.description}")
                content_score = float(np.dot(user_profile_vec, p_vec))
                content_score = max(0.0, min(1.0, (content_score + 1.0) / 2.0))
                if content_score > 0.65 and liked_products:
                    content_reason = f"Similar to your favorite '{liked_products[0].title}'"
            elif p.category in user_pref_categories:
                content_score = 0.8
                content_reason = f"Matches your preferred category: {p.category}"
            else:
                content_score = 0.5

            # Popularity score
            raw_pop = pop_dict.get(p.id, 0.0)
            pop_score = min(1.0, raw_pop / max_pop)

            # Location proximity score
            loc_score = 0.0
            dist_km = None
            loc_reason = None
            if user_lat is not None and user_lng is not None and p.merchant:
                dist_km = haversine_distance_km(user_lat, user_lng, p.merchant.latitude, p.merchant.longitude)
                # Boost if within 15 km
                if dist_km <= 15.0:
                    loc_score = max(0.0, 1.0 - (dist_km / 15.0))
                    loc_reason = f"Available nearby ({dist_km:.1f} km away at {p.merchant.business_name})"
                else:
                    loc_score = 0.1
            else:
                loc_score = 0.3

            # Repetition penalty (prevents viral doom-loops)
            rep_penalty = self.repetition_penalty if p.id in user_viewed_ids else 0.0

            # Exploration noise (discovers new categories)
            explore_bonus = random.uniform(0.0, self.exploration_rate)

            # Combined hybrid score
            final_score = (
                (self.w_content * content_score) +
                (self.w_popularity * pop_score) +
                (self.w_location * loc_score) +
                explore_bonus -
                rep_penalty
            )
            final_score = round(max(0.01, final_score), 4)

            # Generate natural explainable reason
            reasons = []
            if loc_reason:
                reasons.append(loc_reason)
            if content_reason:
                reasons.append(content_reason)
            elif pop_score > 0.5:
                reasons.append(f"Trending in {p.category} with high shopper engagement")
            elif p.merchant and p.merchant.is_verified:
                reasons.append(f"Artisan selection from verified merchant ({p.merchant.trust_score:.0f}% trust score)")
            else:
                reasons.append(f"Curated {p.category} recommendation for you")

            explanation = " • ".join(reasons)

            scored_candidates.append({
                "product": p,
                "score": final_score,
                "distance_km": dist_km,
                "explanation": explanation
            })

        # Sort by final score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = scored_candidates[:limit]

        # Format output
        results = []
        for item in top_candidates:
            prod = item["product"]
            results.append({
                "id": prod.id,
                "title": prod.title,
                "description": prod.description,
                "category": prod.category,
                "price": prod.price,
                "inventory": prod.inventory,
                "image_url": prod.image_url,
                "tags": prod.get_tags(),
                "merchant_id": prod.merchant_id,
                "merchant_name": prod.merchant.business_name if prod.merchant else "Independent Artisan",
                "merchant_city": prod.merchant.city if prod.merchant else "Local",
                "merchant_verified": prod.merchant.is_verified if prod.merchant else False,
                "merchant_trust_score": prod.merchant.trust_score if prod.merchant else 75.0,
                "distance_km": item["distance_km"],
                "recommendation_score": item["score"],
                "explanation": item["explanation"]
            })

        return results

recommender = HybridRecommender()
