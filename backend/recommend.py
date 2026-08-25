#!/usr/bin/env python3
"""
recommend.py — Recommendation engine using cosine similarity on precomputed embeddings.

Load once, query many times. Excludes same media_type by default.

Usage:
    From another module: engine = RecommendationEngine()
                          results = engine.recommend(content_id, top_n=5, target_media=None)
"""

import os
import json
import time
import numpy as np
import pandas as pd
from typing import Optional
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
UNIFIED_CSV = os.path.join(DATA_DIR, "unified_dataset.csv")
EMBEDDINGS_FILE = os.path.join(DATA_DIR, "embeddings.npy")
IDS_FILE = os.path.join(DATA_DIR, "content_ids.json")


class RecommendationEngine:
    """Load precomputed embeddings and provide similarity-based recommendations."""

    def __init__(self):
        self._load_data()

    def _load_data(self):
        """Load dataset, embeddings, and content ID index."""
        if not os.path.exists(EMBEDDINGS_FILE) or not os.path.exists(IDS_FILE):
            raise FileNotFoundError(
                "Embeddings not found. Run `python embed.py` first."
            )

        self.df = pd.read_csv(UNIFIED_CSV)
        self.embeddings = np.load(EMBEDDINGS_FILE)

        with open(IDS_FILE, "r") as f:
            self.content_ids = json.load(f)

        # Build id -> index mapping
        self.id_to_idx = {cid: i for i, cid in enumerate(self.content_ids)}

        # Precompute all pairwise similarities is overkill for ~70 items;
        # we'll compute on-the-fly per query which is plenty fast.
        print(
            f"RecommendationEngine loaded: {len(self.df)} items, "
            f"embeddings shape {self.embeddings.shape}"
        )

    def get_item(self, content_id: str) -> Optional[dict]:
        """Get a single item by content_id."""
        if content_id not in self.id_to_idx:
            return None
        row = self.df[self.df["content_id"] == content_id].iloc[0]
        return row.to_dict()

    def search(self, query: str, media_type: Optional[str] = None, limit: int = 20) -> list[dict]:
        """Search items by title or description substring match."""
        q = query.lower().strip()
        if not q:
            return []

        mask = (
            self.df["title"].str.lower().str.contains(q, na=False)
            | self.df["description"].str.lower().str.contains(q, na=False)
        )
        if media_type and media_type != "all":
            mask = mask & (self.df["media_type"] == media_type.lower())

        results = self.df[mask].head(limit)
        return results.to_dict("records")

    def _get_top_keywords(self, text: str, top_n: int = 5) -> list[str]:
        """Extract top keywords from text by frequency."""
        if not text:
            return []
        words = text.lower().split()
        from collections import Counter
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "need", "dare", "ought",
            "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "above", "below",
            "between", "out", "off", "over", "under", "again", "further", "then",
            "once", "here", "there", "when", "where", "why", "how", "all", "both",
            "each", "few", "more", "most", "other", "some", "such", "no", "nor",
            "not", "only", "own", "same", "so", "than", "too", "very", "just",
            "don", "now", "and", "but", "or", "if", "while", "about", "it", "its",
            "that", "this", "which", "who", "whom", "what", "up", "also", "one",
            "two", "new", "like", "much", "well", "back", "even", "still", "first",
        }
        words = [w for w in words if w not in stop_words and len(w) > 2]
        return [w for w, _ in Counter(words).most_common(top_n)]

    def _generate_why(
        self, source_row: dict, target_row: dict, score: float
    ) -> str:
        """Generate a short explanation of why items are recommended."""
        source_genres = set(
            g.strip().lower() for g in str(source_row.get("genre", "")).split(",") if g.strip()
        )
        target_genres = set(
            g.strip().lower() for g in str(target_row.get("genre", "")).split(",") if g.strip()
        )
        shared = source_genres & target_genres

        source_kw = set(self._get_top_keywords(str(source_row.get("description", ""))))
        target_kw = set(self._get_top_keywords(str(target_row.get("description", ""))))
        shared_kw = source_kw & target_kw

        reasons = []
        if shared:
            reasons.append(f"Shared genres: {', '.join(sorted(shared)[:3])}")
        if shared_kw:
            reasons.append(f"Common themes: {', '.join(sorted(shared_kw)[:3])}")
        if not reasons:
            reasons.append("Semantically similar narrative content")

        score_pct = round(score * 100, 1)
        if score_pct >= 70:
            reasons.insert(0, "Very high")
        elif score_pct >= 50:
            reasons.insert(0, "High")
        else:
            reasons.insert(0, "Moderate")

        return f"{reasons[0]} similarity ({score_pct}%). {'; '.join(reasons[1:])}"

    def recommend(
        self,
        content_id: str,
        top_n: int = 5,
        target_media: Optional[str] = None,
        include_same_media: bool = False,
    ) -> dict:
        """
        Get recommendations for a given content_id.

        Args:
            content_id: The item to recommend similar items for.
            top_n: Number of recommendations to return.
            target_media: Comma-separated target media types (e.g., "book,tv").
                         If None and include_same_media=False, excludes same type.
            include_same_media: If True, includes items of the same media type.

        Returns:
            dict with source item and list of recommendations.
        """
        start_time = time.time()

        if content_id not in self.id_to_idx:
            return {"error": f"Item '{content_id}' not found", "recommendations": []}

        idx = self.id_to_idx[content_id]
        source_embedding = self.embeddings[idx : idx + 1]  # shape (1, dim)
        source_row = self.df.iloc[idx]

        # Compute cosine similarity against all other items
        similarities = sklearn_cosine(source_embedding, self.embeddings)[0]

        # Build candidate mask
        valid_mask = np.ones(len(similarities), dtype=bool)
        valid_mask[idx] = False  # exclude self

        # Media type filtering
        source_type = source_row["media_type"].lower()
        if target_media:
            target_types = [t.strip().lower() for t in target_media.split(",")]
            media_mask = self.df["media_type"].str.lower().isin(target_types)
            valid_mask &= media_mask
        elif not include_same_media:
            # Exclude same media type
            media_mask = self.df["media_type"].str.lower() != source_type
            valid_mask &= media_mask

        # Apply mask
        masked_similarities = similarities.copy()
        masked_similarities[~valid_mask] = -1

        # Get top-N
        top_indices = np.argsort(masked_similarities)[::-1][:top_n]

        recommendations = []
        for rank, rec_idx in enumerate(top_indices):
            score = float(masked_similarities[rec_idx])
            if score < 0:
                break
            target_row = self.df.iloc[rec_idx]
            rec = {
                "content_id": target_row["content_id"],
                "title": target_row["title"],
                "media_type": target_row["media_type"],
                "genre": target_row["genre"],
                "similarity_score": round(score, 4),
                "similarity_pct": round(score * 100, 1),
                "why": self._generate_why(
                    source_row.to_dict(), target_row.to_dict(), score
                ),
                "description": (
                    str(target_row["description"])[:200] + "..."
                    if len(str(target_row["description"])) > 200
                    else str(target_row["description"])
                ),
            }
            recommendations.append(rec)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "source": {
                "content_id": source_row["content_id"],
                "title": source_row["title"],
                "media_type": source_row["media_type"],
                "description": source_row["description"],
                "genre": source_row["genre"],
                "year": int(source_row["year"]) if pd.notna(source_row["year"]) else None,
                "rating": float(source_row["avg_rating"]) if pd.notna(source_row["avg_rating"]) else None,
            },
            "recommendations": recommendations,
            "metadata": {
                "total_items_compared": int(valid_mask.sum()),
                "computation_time_ms": elapsed_ms,
                "include_same_media": include_same_media,
            },
        }

    def get_evaluation_stats(self) -> dict:
        """
        Compute evaluation statistics on the dataset.
        These are prototype-scale metrics, not paper-level benchmarks.
        """
        start_time = time.time()

        # Compute average similarity of top-1 matches for each item
        top1_scores = []
        top5_scores = []
        response_times = []

        sample_size = min(len(self.df), 50)  # Subsample for speed
        np.random.seed(42)
        sample_indices = np.random.choice(len(self.df), sample_size, replace=False)

        for idx in sample_indices:
            t0 = time.time()
            source_emb = self.embeddings[idx : idx + 1]
            sims = sklearn_cosine(source_emb, self.embeddings)[0]

            # Exclude self and same media type
            source_type = self.df.iloc[idx]["media_type"].lower()
            valid_mask = np.ones(len(sims), dtype=bool)
            valid_mask[idx] = False
            valid_mask &= self.df["media_type"].str.lower() != source_type

            masked_sims = sims.copy()
            masked_sims[~valid_mask] = -1

            sorted_sims = np.sort(masked_sims)[::-1]
            top1_scores.append(float(sorted_sims[0]))
            top5_scores.append(float(np.mean(sorted_sims[:5])))

            elapsed = (time.time() - t0) * 1000
            response_times.append(elapsed)

        total_elapsed = time.time() - start_time

        return {
            "dataset_stats": {
                "total_items": len(self.df),
                "movies_tv": int((self.df["media_type"].isin(["movie", "tv"])).sum()),
                "books": int((self.df["media_type"] == "book").sum()),
                "embedding_dimension": int(self.embeddings.shape[1]),
                "model": "all-MiniLM-L6-v2",
            },
            "similarity_metrics": {
                "avg_top1_similarity": round(float(np.mean(top1_scores)), 4),
                "avg_top5_similarity": round(float(np.mean(top5_scores)), 4),
                "min_top1_similarity": round(float(np.min(top1_scores)), 4),
                "max_top1_similarity": round(float(np.max(top1_scores)), 4),
                "std_top1_similarity": round(float(np.std(top1_scores)), 4),
                "sample_size": sample_size,
            },
            "performance_metrics": {
                "avg_query_time_ms": round(float(np.mean(response_times)), 2),
                "max_query_time_ms": round(float(np.max(response_times)), 2),
                "total_eval_time_s": round(total_elapsed, 2),
            },
            "disclaimer": "Prototype-scale metrics computed on sample dataset (~70 items). Not representative of production-scale accuracy.",
        }


# Singleton for API use
_engine: Optional[RecommendationEngine] = None


def get_engine() -> RecommendationEngine:
    """Get or create the singleton RecommendationEngine."""
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
    return _engine
