import os
import json
import logging
from pathlib import Path
from typing import Optional
import faiss
import numpy as np

from app.core.config import settings
from app.services.embeddings.embedder import EMBEDDING_DIM

logger = logging.getLogger(__name__)

class FaissVectorIndex:
    def __init__(self, index_path: Optional[Path] = None, meta_path: Optional[Path] = None):
        self.index_path = index_path or settings.FAISS_INDEX_PATH
        self.meta_path = meta_path or settings.FAISS_METADATA_PATH
        self.dim = EMBEDDING_DIM
        self.index: faiss.IndexFlatIP = faiss.IndexFlatIP(self.dim)
        # Mapping from faiss internal index (0..N-1) to product_id
        self.id_to_product_id: list[int] = []
        self.product_id_to_id: dict[int, int] = {}
        self.color_histograms: dict[int, list[float]] = {}
        self.load()

    def add_product(self, product_id: int, vector: np.ndarray, color_hist: Optional[np.ndarray] = None):
        """
        Adds or updates a product vector in the index with optional color histogram.
        """
        vector = np.array(vector, dtype="float32").reshape(1, self.dim)
        faiss.normalize_L2(vector)

        if product_id in self.product_id_to_id:
            self.remove_product(product_id)

        current_idx = len(self.id_to_product_id)
        self.index.add(vector)
        self.id_to_product_id.append(product_id)
        self.product_id_to_id[product_id] = current_idx
        COLOR_DIM = 64
        if color_hist is not None:
            self.color_histograms[product_id] = [float(x) for x in color_hist]
        else:
            self.color_histograms[product_id] = [float(1.0 / (COLOR_DIM ** 0.5))] * COLOR_DIM
        self.save()

    def search_similar(self, query_vector: np.ndarray, top_k: int = 10, min_score: float = 0.0) -> list[dict]:
        """
        Searches nearest neighbors by cosine similarity.
        Returns: list of {"product_id": int, "score": float}
        """
        if self.index.ntotal == 0 or len(self.id_to_product_id) == 0:
            return []

        query = np.array(query_vector, dtype="float32").reshape(1, self.dim)
        faiss.normalize_L2(query)

        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.id_to_product_id):
                continue
            score = float(dist)
            if score >= min_score:
                results.append({
                    "product_id": self.id_to_product_id[idx],
                    "score": round(score, 4)
                })
        return results

    def search_similar_visual(
        self,
        query_vector: np.ndarray,
        query_color: Optional[np.ndarray] = None,
        top_k: int = 10,
        min_score: float = 0.15
    ) -> list[dict]:
        """
        Searches nearest neighbors using deep visual features and color harmony reranking.
        """
        if self.index.ntotal == 0 or len(self.id_to_product_id) == 0:
            return []

        query = np.array(query_vector, dtype="float32").reshape(1, self.dim)
        faiss.normalize_L2(query)

        search_k = min(top_k * 4, self.index.ntotal)
        distances, indices = self.index.search(query, search_k)

        candidates = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.id_to_product_id):
                continue
            pid = self.id_to_product_id[idx]
            clip_score = float(dist)

            color_sim = 0.0
            if query_color is not None and pid in self.color_histograms:
                p_col = np.array(self.color_histograms[pid], dtype=np.float32)
                q_col = np.array(query_color, dtype=np.float32)
                if p_col.shape == q_col.shape:
                    color_sim = max(0.0, float(np.dot(q_col, p_col)))
                    combined_score = 0.70 * clip_score + 0.30 * color_sim
                else:
                    combined_score = clip_score
            else:
                combined_score = clip_score

            if combined_score >= min_score:
                candidates.append({
                    "product_id": pid,
                    "score": round(combined_score, 4),
                    "clip_score": round(clip_score, 4),
                    "color_score": round(color_sim, 4)
                })

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:top_k]

    def sync_catalogue_visual_index(self, db, embedder):
        """
        Synchronizes FAISS vector index with authentic visual embeddings of all catalogue products.
        """
        from app.database.models import Product
        products = db.query(Product).filter(Product.is_active == True).all()

        catalogue_dir = settings.DATA_DIR / "catalogue_images"
        catalogue_dir.mkdir(parents=True, exist_ok=True)

        self.index = faiss.IndexFlatIP(self.dim)
        self.id_to_product_id = []
        self.product_id_to_id = {}
        self.color_histograms = {}

        synced_count = 0
        for p in products:
            img_path = catalogue_dir / f"product_{p.id}.jpg"
            if img_path.exists() and img_path.stat().st_size > 1000:
                vec = embedder.embed_image(str(img_path))
                color_hist = embedder.get_color_histogram(str(img_path))
            else:
                # Text features fallback
                text_features = f"{p.title} {p.category} {p.description} {' '.join(p.get_tags())}"
                vec = embedder.embed_text(text_features)
                color_hist = None

            self.add_product(p.id, vec, color_hist=color_hist)
            p.embedding_id = p.id
            synced_count += 1

        db.commit()
        logger.info(f"Synchronized visual FAISS index with {synced_count} catalogue products.")
        return synced_count

    def remove_product(self, product_id: int):
        """Removes a product by rebuilding the index without it."""
        if product_id not in self.product_id_to_id:
            return

        target_idx = self.product_id_to_id[product_id]
        total = self.index.ntotal
        
        remaining_vectors = []
        new_ids = []
        for i in range(total):
            if i != target_idx:
                vec = self.index.reconstruct(i)
                remaining_vectors.append(vec)
                new_ids.append(self.id_to_product_id[i])

        self.index = faiss.IndexFlatIP(self.dim)
        self.id_to_product_id = []
        self.product_id_to_id = {}

        if remaining_vectors:
            mat = np.array(remaining_vectors, dtype="float32")
            self.index.add(mat)
            self.id_to_product_id = new_ids
            self.product_id_to_id = {pid: i for i, pid in enumerate(new_ids)}

        if product_id in self.color_histograms:
            del self.color_histograms[product_id]

        self.save()

    def save(self):
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.index_path))
            with open(self.meta_path, "w", encoding="utf-8") as f:
                json.dump({
                    "id_to_product_id": self.id_to_product_id,
                    "color_histograms": self.color_histograms
                }, f, indent=2)
            logger.debug(f"Saved FAISS index with {self.index.ntotal} items.")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}", exc_info=True)

    def load(self):
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
                self.index = faiss.read_index(str(self.index_path))
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.id_to_product_id = meta.get("id_to_product_id", [])
                    self.product_id_to_id = {pid: i for i, pid in enumerate(self.id_to_product_id)}
                    raw_colors = meta.get("color_histograms", {})
                    self.color_histograms = {int(k): v for k, v in raw_colors.items()}
                    for pid in self.id_to_product_id:
                        if pid not in self.color_histograms:
                            self.color_histograms[pid] = [float(1.0 / (self.dim ** 0.5))] * self.dim
                logger.info(f"Loaded persistent FAISS index with {self.index.ntotal} items and {len(self.color_histograms)} color profiles.")
            else:
                self.index = faiss.IndexFlatIP(self.dim)
                self.id_to_product_id = []
                self.product_id_to_id = {}
                self.color_histograms = {}
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}. Creating new index.", exc_info=True)
            self.index = faiss.IndexFlatIP(self.dim)
            self.id_to_product_id = []
            self.product_id_to_id = {}
            self.color_histograms = {}

vector_index = FaissVectorIndex()
