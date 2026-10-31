import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.session import init_db, SessionLocal
from app.database.models import Product
from app.services.vector_search.faiss_index import vector_index
from app.services.embeddings.embedder import embedder

# API Routers
from app.api.auth import router as auth_router
from app.api.merchants import router as merchants_router
from app.api.products import router as products_router
from app.api.videos import router as videos_router
from app.api.search import router as search_router
from app.api.recommendations import router as recommendations_router
from app.api.location import router as location_router
from app.api.assistant import router as assistant_router
from app.api.fraud import router as fraud_router
from app.api.analytics import router as analytics_router
from app.api.admin import router as admin_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("scrollix")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables and seed data
    logger.info("Initializing Scrollix AI database...")
    init_db()

    # Synchronize FAISS vector index with active products
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.is_active == True).all()
        if vector_index.index.ntotal != len(products) or len(vector_index.color_histograms) == 0:
            logger.info("Synchronizing visual embeddings for catalogue in FAISS...")
            vector_index.sync_catalogue_visual_index(db, embedder)
        else:
            logger.info(f"FAISS visual index up to date with {vector_index.index.ntotal} items and {len(vector_index.color_histograms)} visual profiles.")
    finally:
        db.close()

    yield
    # Shutdown clean up
    logger.info("Shutting down Scrollix AI backend cleanly.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Social Commerce & Location-Aware Video Recommendations Engine",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media uploads directory
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(merchants_router, prefix=settings.API_V1_STR)
app.include_router(products_router, prefix=settings.API_V1_STR)
app.include_router(videos_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(recommendations_router, prefix=settings.API_V1_STR)
app.include_router(location_router, prefix=settings.API_V1_STR)
app.include_router(assistant_router, prefix=settings.API_V1_STR)
app.include_router(fraud_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "api_docs": "/docs"
    }

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "Scrollix AI Backend",
        "faiss_total": vector_index.index.ntotal
    }

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
