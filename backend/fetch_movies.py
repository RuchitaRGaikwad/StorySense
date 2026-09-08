#!/usr/bin/env python3
"""
fetch_movies.py — Fetch ~2,000 real movies from TMDB with thematic diversity.

Uses TMDB Discover API to fetch movies across many genres,
ensuring broad narrative coverage for cross-media recommendations.

Usage:
    cd backend
    source venv/bin/activate
    python fetch_movies.py
"""

import os
import sys
import json
import time
import csv
import requests
import pandas as pd
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ENV_FILE = os.path.join(BASE_DIR, ".env")
OUTPUT_CSV = os.path.join(DATA_DIR, "movies_real.csv")
CACHE_FILE = os.path.join(DATA_DIR, "tmdb_movie_cache.json")

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# TMDB genre IDs and target counts for thematic balance
GENRE_TARGETS = {
    878: ("Science Fiction", 130),
    28: ("Action", 110),
    53: ("Thriller", 110),
    18: ("Drama", 130),
    80: ("Crime", 100),
    27: ("Horror", 90),
    12: ("Adventure", 100),
    14: ("Fantasy", 90),
    10749: ("Romance", 90),
    9648: ("Mystery", 90),
    10752: ("War", 80),
    36: ("History", 80),
    35: ("Comedy", 110),
    16: ("Animation", 70),
    99: ("Documentary", 60),
    10751: ("Family", 60),
    37: ("Western", 50),
    10402: ("Music", 50),
}

# Additional keyword-based queries for thematic depth
KEYWORD_QUERIES = [
    ({"with_keywords": "9882", "with_genres": "878"}, "AI / Artificial Intelligence", 40),
    ({"with_keywords": "4565", "with_genres": "878"}, "Time Travel", 40),
    ({"with_keywords": "1432|612", "with_genres": "878"}, "Space / Astronaut", 50),
    ({"with_keywords": "3801", "with_genres": "878"}, "Dystopia", 50),
    ({"with_keywords": "818", "with_genres": "18"}, "Coming of Age", 50),
    ({"with_keywords": "10084|9715"}, "Survival", 50),
    ({"with_keywords": "11322|209891"}, "Espionage / Spy", 40),
    ({"with_keywords": "4344", "with_genres": "18"}, "Psychology / Mental Health", 40),
]

RATE_DELAY = 0.06  # ~16 req/s, well within 40/s limit


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def fetch_discover_page(api_key, params, page=1):
    """Fetch one page from TMDB Discover endpoint."""
    p = {
        "api_key": api_key,
        "language": "en-US",
        "sort_by": "vote_average.desc",
        "vote_count.gte": 50,
        "include_adult": "false",
        "page": page,
        **params,
    }
    try:
        resp = requests.get(f"{TMDB_BASE}/discover/movie", params=p, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"  ⚠ TMDB request failed: {e}")
        return {"results": [], "total_pages": 0}


def fetch_genre_list(api_key):
    """Fetch TMDB genre ID->name mapping."""
    resp = requests.get(f"{TMDB_BASE}/genre/movie/list",
                        params={"api_key": api_key, "language": "en-US"}, timeout=10)
    resp.raise_for_status()
    return {g["id"]: g["name"] for g in resp.json()["genres"]}


def process_movie(movie, genre_map):
    """Extract relevant fields from a TMDB movie result."""
    overview = (movie.get("overview") or "").strip()
    if not overview or len(overview) < 30:
        return None

    tmdb_id = movie["id"]
    title = movie.get("title") or movie.get("original_title", "")
    if not title:
        return None

    release_date = movie.get("release_date", "")
    year = int(release_date[:4]) if release_date and len(release_date) >= 4 else 0

    genre_ids = movie.get("genre_ids", [])
    genres = ", ".join(genre_map.get(gid, "") for gid in genre_ids if gid in genre_map)

    poster_path = movie.get("poster_path")
    poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else ""

    return {
        "tmdb_id": tmdb_id,
        "title": title,
        "media_type": "movie",
        "description": overview,
        "genre": genres,
        "year": year,
        "avg_rating": round(float(movie.get("vote_average", 0)), 1),
        "poster_url": poster_url,
        "vote_count": movie.get("vote_count", 0),
        "popularity": movie.get("popularity", 0),
    }


def main():
    print("=" * 60)
    print("StorySense — Fetch Real Movies from TMDB")
    print("=" * 60)

    load_dotenv(ENV_FILE)
    api_key = os.getenv("TMDB_API_KEY", "")
    if not api_key or api_key == "your_tmdb_api_key_here":
        print("✗ TMDB_API_KEY not set. Add it to backend/.env")
        sys.exit(1)
    print(f"✓ TMDB API key loaded")

    genre_map = fetch_genre_list(api_key)
    print(f"✓ Loaded {len(genre_map)} TMDB genres")

    cache = load_cache()
    seen_ids = set()
    all_movies = []

    # Restore from cache if available
    if "movies" in cache:
        all_movies = cache["movies"]
        seen_ids = {m["tmdb_id"] for m in all_movies}
        print(f"📦 Restored {len(all_movies)} movies from cache")

    target_total = 2200  # Fetch slightly more, deduplicate down to ~2000

    if len(all_movies) < target_total:
        # ── Genre-based discovery ──────────────────────────────────────
        for genre_id, (genre_name, target_count) in GENRE_TARGETS.items():
            if len(all_movies) >= target_total:
                break

            print(f"\n🎬 Fetching: {genre_name} (target: {target_count})...")
            added = 0
            for page in range(1, 12):  # Up to 11 pages (220 results max)
                if added >= target_count:
                    break

                data = fetch_discover_page(api_key, {"with_genres": str(genre_id)}, page)
                results = data.get("results", [])
                if not results:
                    break

                for movie in results:
                    if movie["id"] in seen_ids:
                        continue
                    processed = process_movie(movie, genre_map)
                    if processed:
                        all_movies.append(processed)
                        seen_ids.add(movie["id"])
                        added += 1

                time.sleep(RATE_DELAY)

            print(f"  ✓ Added {added} movies ({len(all_movies)} total)")

            # Save cache periodically
            if len(all_movies) % 200 < 50:
                cache["movies"] = all_movies
                save_cache(cache)

        # ── Keyword-based queries for thematic depth ───────────────────
        for params, label, target in KEYWORD_QUERIES:
            if len(all_movies) >= target_total:
                break

            print(f"\n🔑 Keyword query: {label} (target: {target})...")
            added = 0
            for page in range(1, 6):
                if added >= target:
                    break

                data = fetch_discover_page(api_key, params, page)
                results = data.get("results", [])
                if not results:
                    break

                for movie in results:
                    if movie["id"] in seen_ids:
                        continue
                    processed = process_movie(movie, genre_map)
                    if processed:
                        all_movies.append(processed)
                        seen_ids.add(movie["id"])
                        added += 1

                time.sleep(RATE_DELAY)

            print(f"  ✓ Added {added} movies ({len(all_movies)} total)")

    # Save final cache
    cache["movies"] = all_movies
    save_cache(cache)

    # Deduplicate and trim to 2000
    print(f"\n📊 Pre-dedup count: {len(all_movies)}")

    # Deduplicate by tmdb_id
    deduped = {}
    for m in all_movies:
        tid = m["tmdb_id"]
        if tid not in deduped:
            deduped[tid] = m

    movies_list = list(deduped.values())

    # Sort by vote_count (prefer well-known movies) and trim
    movies_list.sort(key=lambda x: x["vote_count"], reverse=True)
    movies_list = movies_list[:2000]

    # Assign content IDs
    for i, m in enumerate(movies_list):
        m["content_id"] = f"MOV_{i+1:04d}"

    # Save to CSV
    df = pd.DataFrame(movies_list)
    columns = ["content_id", "title", "media_type", "description", "genre",
               "year", "avg_rating", "poster_url", "tmdb_id"]
    df[columns].to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_NONNUMERIC)

    # Stats
    with_poster = (df["poster_url"] != "").sum()
    with_desc = (df["description"].str.len() > 30).sum()
    genres = df["genre"].str.split(", ").explode().value_counts()

    print(f"\n{'=' * 60}")
    print(f"✓ Saved {len(df)} real movies to {OUTPUT_CSV}")
    print(f"  With poster: {with_poster}")
    print(f"  With description (>30 chars): {with_desc}")
    print(f"  Year range: {df['year'].min()} – {df['year'].max()}")
    print(f"\n  Genre distribution (top 15):")
    for genre, count in genres.head(15).items():
        print(f"    {genre}: {count}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
