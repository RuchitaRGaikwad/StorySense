#!/usr/bin/env python3
"""
enrich_posters.py — Fetch poster/cover images for movies, TV shows, and books.

Uses:
  - TMDB API for movies and TV shows (requires TMDB_API_KEY in .env)
  - Open Library Search API for books (no key needed)

This script is meant to be run MANUALLY (not on every app startup).
Results are cached in data/poster_cache.json so the APIs are not called repeatedly.

Usage:
    cd backend
    python enrich_posters.py

The script updates unified_dataset.csv with a `poster_url` column.
It does NOT modify embeddings.npy or any NLP/recommendation logic.
"""

import os
import sys
import json
from typing import Optional
import time
import re
import requests
import pandas as pd
from dotenv import load_dotenv

# ── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UNIFIED_CSV = os.path.join(DATA_DIR, "unified_dataset.csv")
CACHE_FILE = os.path.join(DATA_DIR, "poster_cache.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

# ── Configuration ────────────────────────────────────────────────────────────

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
OPENLIBRARY_SEARCH = "https://openlibrary.org/search.json"
OPENLIBRARY_COVER = "https://covers.openlibrary.org/b/id"

# Rate limit: pause between API batches
TMDB_DELAY = 0.08       # ~12 req/sec (well within 40/sec limit)
OL_DELAY = 0.15          # Be polite to Open Library
BATCH_LOG_INTERVAL = 50   # Print progress every N items


# ── Cache ────────────────────────────────────────────────────────────────────

def load_cache() -> dict:
    """Load cached API results from disk."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict):
    """Save cache to disk."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


# ── TMDB (Movies & TV) ──────────────────────────────────────────────────────

def normalize_title(title: str) -> str:
    """Lowercase, strip punctuation for fuzzy matching."""
    return re.sub(r"[^\w\s]", "", title.lower()).strip()


def tmdb_search_movie(title: str, year: int, api_key: str) -> Optional[str]:
    """Search TMDB for a movie poster URL. Returns URL or None."""
    params = {"api_key": api_key, "query": title, "language": "en-US"}
    if year and year > 0:
        params["year"] = year

    try:
        resp = requests.get(f"{TMDB_BASE}/search/movie", params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except requests.RequestException as e:
        print(f"    ⚠ TMDB request failed for '{title}': {e}")
        return None

    if not results:
        return None

    # Try exact title match first
    norm_title = normalize_title(title)
    for r in results:
        r_title = normalize_title(r.get("title", ""))
        r_year = (r.get("release_date") or "")[:4]
        year_match = not year or not r_year or abs(int(r_year or 0) - year) <= 1

        if r_title == norm_title and year_match and r.get("poster_path"):
            return f"{TMDB_IMAGE_BASE}{r['poster_path']}"

    # Fall back to first result if title is close enough
    first = results[0]
    if first.get("poster_path") and normalize_title(first.get("title", "")) == norm_title:
        return f"{TMDB_IMAGE_BASE}{first['poster_path']}"

    return None


def tmdb_search_tv(title: str, year: int, api_key: str) -> Optional[str]:
    """Search TMDB for a TV show poster URL. Returns URL or None."""
    params = {"api_key": api_key, "query": title, "language": "en-US"}
    if year and year > 0:
        params["first_air_date_year"] = year

    try:
        resp = requests.get(f"{TMDB_BASE}/search/tv", params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except requests.RequestException as e:
        print(f"    ⚠ TMDB request failed for '{title}': {e}")
        return None

    if not results:
        return None

    norm_title = normalize_title(title)
    for r in results:
        r_title = normalize_title(r.get("name", ""))
        r_year = (r.get("first_air_date") or "")[:4]
        year_match = not year or not r_year or abs(int(r_year or 0) - year) <= 1

        if r_title == norm_title and year_match and r.get("poster_path"):
            return f"{TMDB_IMAGE_BASE}{r['poster_path']}"

    first = results[0]
    if first.get("poster_path") and normalize_title(first.get("name", "")) == norm_title:
        return f"{TMDB_IMAGE_BASE}{first['poster_path']}"

    return None


# ── Open Library (Books) ─────────────────────────────────────────────────────

def openlibrary_search_book(title: str, author: str = "", year: int = 0) -> Optional[str]:
    """Search Open Library for a book cover URL. Returns URL or None."""
    params = {"title": title, "limit": 5}
    if author:
        params["author"] = author

    try:
        resp = requests.get(OPENLIBRARY_SEARCH, params=params, timeout=15)
        resp.raise_for_status()
        docs = resp.json().get("docs", [])
    except requests.RequestException as e:
        print(f"    ⚠ Open Library request failed for '{title}': {e}")
        return None

    if not docs:
        return None

    norm_title = normalize_title(title)

    for doc in docs:
        doc_title = normalize_title(doc.get("title", ""))
        cover_i = doc.get("cover_i")

        if not cover_i:
            continue

        # Check title match
        title_match = (doc_title == norm_title) or (norm_title in doc_title) or (doc_title in norm_title)

        if not title_match:
            continue

        # Check year if available (within ±2 years for books)
        if year and year > 0:
            pub_year = doc.get("first_publish_year")
            if pub_year and abs(int(pub_year) - year) > 2:
                continue

        # Check author if available
        if author:
            doc_authors = [a.lower() for a in doc.get("author_name", [])]
            author_lower = author.lower()
            # Check if any part of the author name matches
            author_match = any(
                author_lower in a or a in author_lower
                for a in doc_authors
            )
            if not author_match:
                # Author mismatch — skip this result but don't disqualify
                # (could be a reprint under a different name)
                pass

        return f"{OPENLIBRARY_COVER}/{cover_i}-L.jpg"

    # No confident match found
    return None


# ── Main Enrichment Logic ────────────────────────────────────────────────────

def enrich_posters():
    """Main enrichment function."""
    print("=" * 60)
    print("StorySense — Poster / Cover Enrichment")
    print("=" * 60)

    # Load environment
    load_dotenv(ENV_FILE)
    tmdb_key = os.getenv("TMDB_API_KEY", "")
    if not tmdb_key or tmdb_key == "your_tmdb_api_key_here":
        print("\n⚠  TMDB_API_KEY not set in backend/.env")
        print("   Movies/TV posters will be SKIPPED.")
        print("   To fix: copy .env.example to .env and paste your real key.")
        tmdb_key = None
    else:
        print(f"✓ TMDB API key loaded ({tmdb_key[:4]}...{tmdb_key[-4:]})")

    # Load unified dataset
    if not os.path.exists(UNIFIED_CSV):
        print(f"\n✗ {UNIFIED_CSV} not found. Run prepare_dataset.py first.")
        sys.exit(1)

    df = pd.read_csv(UNIFIED_CSV)
    print(f"\n📊 Loaded {len(df)} items from unified_dataset.csv")

    # Ensure poster_url column exists
    if "poster_url" not in df.columns:
        df["poster_url"] = ""
    df["poster_url"] = df["poster_url"].fillna("")

    # Load cache
    cache = load_cache()
    print(f"📦 Cache: {len(cache)} entries loaded")

    # ── Enrich Movies & TV ───────────────────────────────────────────────
    if tmdb_key:
        movies_tv = df[df["media_type"].isin(["movie", "tv"])]
        need_poster = movies_tv[movies_tv["poster_url"] == ""]
        print(f"\n🎬 Movies/TV: {len(need_poster)} items need posters (of {len(movies_tv)} total)")

        enriched = 0
        skipped = 0
        for i, (idx, row) in enumerate(need_poster.iterrows()):
            cid = row["content_id"]

            # Check cache first
            if cid in cache:
                url = cache[cid]
                if url:
                    df.at[idx, "poster_url"] = url
                    enriched += 1
                else:
                    skipped += 1
                continue

            # Call TMDB
            title = row["title"]
            year = int(row["year"]) if pd.notna(row["year"]) and row["year"] > 0 else 0
            media = row["media_type"]

            if media == "movie":
                url = tmdb_search_movie(title, year, tmdb_key)
            else:
                url = tmdb_search_tv(title, year, tmdb_key)

            # Store in cache (even None → empty string)
            cache[cid] = url or ""
            if url:
                df.at[idx, "poster_url"] = url
                enriched += 1
            else:
                skipped += 1

            # Progress logging
            if (i + 1) % BATCH_LOG_INTERVAL == 0:
                print(f"    ... processed {i + 1}/{len(need_poster)} ({enriched} found, {skipped} no match)")
                save_cache(cache)  # Periodic save

            time.sleep(TMDB_DELAY)

        print(f"  ✓ TMDB done: {enriched} posters found, {skipped} no match")
        save_cache(cache)

    # ── Enrich Books ─────────────────────────────────────────────────────
    # Load raw books.csv to get author info (not in unified dataset)
    books_csv = os.path.join(DATA_DIR, "books.csv")
    author_map = {}
    if os.path.exists(books_csv):
        books_raw = pd.read_csv(books_csv)
        for _, row in books_raw.iterrows():
            if pd.notna(row.get("authors")):
                author_map[row["content_id"]] = str(row["authors"])

    books = df[df["media_type"] == "book"]
    need_cover = books[books["poster_url"] == ""]
    print(f"\n📚 Books: {len(need_cover)} items need covers (of {len(books)} total)")

    enriched = 0
    skipped = 0
    for i, (idx, row) in enumerate(need_cover.iterrows()):
        cid = row["content_id"]

        # Check cache first
        if cid in cache:
            url = cache[cid]
            if url:
                df.at[idx, "poster_url"] = url
                enriched += 1
            else:
                skipped += 1
            continue

        # Call Open Library
        title = row["title"]
        year = int(row["year"]) if pd.notna(row["year"]) and row["year"] > 0 else 0
        author = author_map.get(cid, "")

        url = openlibrary_search_book(title, author, year)

        cache[cid] = url or ""
        if url:
            df.at[idx, "poster_url"] = url
            enriched += 1
        else:
            skipped += 1

        if (i + 1) % BATCH_LOG_INTERVAL == 0:
            print(f"    ... processed {i + 1}/{len(need_cover)} ({enriched} found, {skipped} no match)")
            save_cache(cache)

        time.sleep(OL_DELAY)

    print(f"  ✓ Open Library done: {enriched} covers found, {skipped} no match")
    save_cache(cache)

    # ── Save updated dataset ─────────────────────────────────────────────
    df.to_csv(UNIFIED_CSV, index=False)
    total_with_poster = (df["poster_url"] != "").sum()
    print(f"\n{'=' * 60}")
    print(f"✓ Enrichment complete!")
    print(f"  {total_with_poster}/{len(df)} items now have poster URLs")
    print(f"  Cache saved: {len(cache)} entries")
    print(f"  Dataset saved: {UNIFIED_CSV}")
    print(f"\n  ⚠ embeddings.npy was NOT modified")
    print(f"  Start the app with: uvicorn main:app --reload --port 8000")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    enrich_posters()
