import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings

# Base directories
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
    WORKSPACE_DIR = BASE_DIR.parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    WORKSPACE_DIR = BASE_DIR.parent

# User-data directory for persistence (portable mode uses ./data, packaged mode can use %APPDATA%/ScrollixAI)
DEFAULT_DATA_DIR = os.environ.get(
    "SCROLLIX_DATA_DIR",
    str(WORKSPACE_DIR / "data")
)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Scrollix AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Storage directories
    DATA_DIR: Path = Path(DEFAULT_DATA_DIR)
    UPLOADS_DIR: Path = Path(DEFAULT_DATA_DIR) / "uploads"
    FAISS_DIR: Path = Path(DEFAULT_DATA_DIR) / "faiss_index"
    MODELS_DIR: Path = BASE_DIR / "models"
    
    # Model files
    YOLO_MODEL_PATH: Path = BASE_DIR / "models" / "yolo11n.pt"
    FAISS_INDEX_PATH: Path = Path(DEFAULT_DATA_DIR) / "faiss_index" / "products.index"
    FAISS_METADATA_PATH: Path = Path(DEFAULT_DATA_DIR) / "faiss_index" / "products_meta.json"
    
    # Database
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{Path(DEFAULT_DATA_DIR) / 'scrollix.db'}"
    )
    
    # Security & JWT
    SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "scrollix-super-secret-production-key-2026-safe-default")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Optional Cloud APIs (Free tier / User provided)
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    FIREBASE_ENABLED: bool = os.environ.get("FIREBASE_ENABLED", "false").lower() == "true"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "electron://*",
        "file://*"
    ]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
settings.FAISS_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
