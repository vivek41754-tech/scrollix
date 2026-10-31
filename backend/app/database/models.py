import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="customer")  # customer, merchant, admin
    avatar_url = Column(String(500), nullable=True)
    preferences_json = Column(Text, default="{}")  # Preferred categories, tags
    created_at = Column(DateTime, default=get_utc_now)

    merchant = relationship("Merchant", back_populates="user", uselist=False, cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def get_preferences(self) -> dict:
        try:
            return json.loads(self.preferences_json or "{}")
        except Exception:
            return {}

    def set_preferences(self, data: dict):
        self.preferences_json = json.dumps(data)


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    business_name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="Retail")
    address = Column(String(255), nullable=True)
    city = Column(String(100), index=True, default="")
    latitude = Column(Float, nullable=False, default=0.0)
    longitude = Column(Float, nullable=False, default=0.0)
    phone = Column(String(50), nullable=True)
    is_verified = Column(Boolean, default=False)
    trust_score = Column(Float, default=75.0)  # 0 to 100
    created_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="merchant")
    products = relationship("Product", back_populates="merchant", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True, default="General")
    price = Column(Float, nullable=False, default=0.0)
    inventory = Column(Integer, default=10)
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    tags_json = Column(Text, default="[]")  # e.g. ["shoes", "sneakers", "leather"]
    embedding_id = Column(Integer, nullable=True, index=True)  # FAISS index ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)

    merchant = relationship("Merchant", back_populates="products")
    interactions = relationship("Interaction", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

    def get_tags(self) -> list[str]:
        try:
            return json.loads(self.tags_json or "[]")
        except Exception:
            return []

    def set_tags(self, tags: list[str]):
        self.tags_json = json.dumps(tags)


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    duration = Column(Float, default=0.0)
    # detections_json structure: [{"timestamp": 1.2, "box": [x1, y1, x2, y2], "label": "shoe", "confidence": 0.88, "product_id": 1}]
    detections_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=get_utc_now)

    interactions = relationship("Interaction", back_populates="video", cascade="all, delete-orphan")

    def get_detections(self) -> list[dict]:
        try:
            return json.loads(self.detections_json or "[]")
        except Exception:
            return []

    def set_detections(self, detections: list[dict]):
        self.detections_json = json.dumps(detections)


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=True)
    interaction_type = Column(String(50), index=True, nullable=False)  # view, like, click, search, purchase_intent
    dwell_time = Column(Float, default=0.0)  # seconds watched or stayed
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=get_utc_now, index=True)

    user = relationship("User", back_populates="interactions")
    product = relationship("Product", back_populates="interactions")
    video = relationship("Video", back_populates="interactions")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, default=5)
    comment = Column(Text, nullable=False)
    sentiment_score = Column(Float, default=0.0)  # -1.0 to +1.0
    sentiment_label = Column(String(20), default="positive")  # positive, neutral, negative
    created_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")


class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String(50), nullable=False)  # merchant, product, user
    target_id = Column(Integer, nullable=False, index=True)
    risk_score = Column(Float, nullable=False, default=0.0)  # 0 to 100
    reasons_json = Column(Text, default="[]")  # list of explainable reason strings
    status = Column(String(50), default="pending")  # pending, approved, dismissed
    flagged_at = Column(DateTime, default=get_utc_now)
    resolved_at = Column(DateTime, nullable=True)

    def get_reasons(self) -> list[str]:
        try:
            return json.loads(self.reasons_json or "[]")
        except Exception:
            return []

    def set_reasons(self, reasons: list[str]):
        self.reasons_json = json.dumps(reasons)


class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
