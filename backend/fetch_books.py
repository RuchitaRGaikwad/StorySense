#!/usr/bin/env python3
"""
fetch_books.py — Fetch ~2,000 real books from Open Library with thematic diversity.

Uses Open Library Search API with curated keyword queries matching
the same narrative themes as the movie dataset, ensuring
meaningful cross-media semantic overlap.

Usage:
    cd backend
    source venv/bin/activate
    python fetch_books.py
"""

import os
import sys
import json
import time
import csv
import re
import requests
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_CSV = os.path.join(DATA_DIR, "books_real.csv")
SEARCH_CACHE = os.path.join(DATA_DIR, "ol_search_cache.json")
WORKS_CACHE = os.path.join(DATA_DIR, "ol_works_cache.json")

OL_SEARCH = "https://openlibrary.org/search.json"
OL_WORKS = "https://openlibrary.org"
OL_COVER_BASE = "https://covers.openlibrary.org/b/id"

SEARCH_DELAY = 0.2  # Be respectful to Open Library
WORKS_DELAY = 0.15

# Curated keyword queries — designed to overlap with movie genre themes
# Each query: (search_query, subject_filter, target_count)
SEARCH_QUERIES = [
    # Science Fiction & related
    ("science fiction", "science_fiction", 120),
    ("dystopia novel", "dystopia", 60),
    ("space opera", "science_fiction", 50),
    ("cyberpunk", "science_fiction", 40),
    ("artificial intelligence fiction", "science_fiction", 40),
    ("time travel novel", "science_fiction", 40),
    ("robot android fiction", "science_fiction", 30),
    ("alien invasion", "science_fiction", 30),
    ("post apocalyptic fiction", "science_fiction", 40),
    ("space exploration novel", "science_fiction", 30),

    # Fantasy
    ("fantasy epic", "fantasy", 80),
    ("dark fantasy", "fantasy", 40),
    ("magic wizard fiction", "fantasy", 50),
    ("dragon fantasy novel", "fantasy", 30),
    ("urban fantasy", "fantasy", 30),

    # Mystery & Crime
    ("mystery detective", "mystery", 80),
    ("crime thriller", "crime", 70),
    ("serial killer novel", "thriller", 40),
    ("murder mystery", "mystery", 50),
    ("heist crime fiction", "crime", 30),
    ("forensic thriller", "thriller", 30),

    # Thriller & Suspense
    ("psychological thriller", "thriller", 60),
    ("political thriller", "thriller", 40),
    ("espionage spy novel", "spy_fiction", 50),
    ("legal thriller", "thriller", 30),
    ("conspiracy thriller", "thriller", 30),

    # Horror
    ("horror supernatural", "horror", 60),
    ("ghost story fiction", "horror", 40),
    ("gothic horror novel", "horror", 40),
    ("cosmic horror lovecraft", "horror", 30),

    # Romance
    ("romance novel", "romance", 60),
    ("historical romance fiction", "romance", 40),
    ("love story literary", "romance", 30),

    # War & History
    ("war novel fiction", "war", 60),
    ("world war fiction", "war", 40),
    ("historical fiction", "historical_fiction", 70),
    ("ancient history fiction", "historical_fiction", 30),
    ("medieval fiction", "historical_fiction", 30),

    # Drama & Literary Fiction
    ("literary fiction", "fiction", 60),
    ("family saga novel", "fiction", 40),
    ("social novel", "fiction", 40),
    ("coming of age novel", "fiction", 60),

    # Adventure & Survival
    ("adventure fiction", "adventure", 60),
    ("survival novel", "adventure", 40),
    ("exploration expedition fiction", "adventure", 30),
    ("pirate adventure", "adventure", 20),

    # Biography & Memoir
    ("biography memoir", "biography", 50),
    ("autobiography", "biography", 30),

    # Comedy & Satire
    ("comedy humor fiction", "humor", 40),
    ("satire novel", "humor", 30),

    # Psychology & Philosophy
    ("psychological fiction", "fiction", 40),
    ("philosophical novel", "fiction", 30),

    # Technology & Science
    ("technology future fiction", "science_fiction", 30),
    ("science discovery nonfiction", None, 20),

    # Classics that cross many themes
    ("classic literature fiction", "fiction", 60),
    ("Pulitzer prize fiction", None, 40),
    ("Booker prize", None, 30),
    ("Hugo award winner", "science_fiction", 30),
    ("Nebula award", "science_fiction", 20),
]


def load_json_cache(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_json_cache(cache, path):
    with open(path, "w") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def clean_description(desc):
    """Clean up Open Library description text."""
    if not desc:
        return ""
    if isinstance(desc, dict):
        desc = desc.get("value", "")
    desc = str(desc).strip()
    # Remove HTML
    desc = re.sub(r"<[^>]+>", "", desc)
    # Remove [source] citations
    desc = re.sub(r"\[source\]|\(\[source\]\)", "", desc)
    # Remove URLs
    desc = re.sub(r"https?://\S+", "", desc)
    # Normalize whitespace
    desc = re.sub(r"\s+", " ", desc).strip()
    # Remove common prefixes like "----------"
    desc = re.sub(r"^[-=_]{3,}", "", desc).strip()
    return desc


def search_books(query, limit=100):
    """Search Open Library."""
    params = {
        "q": query,
        "limit": limit,
        "fields": "key,title,author_name,first_publish_year,cover_i,subject,isbn,number_of_pages_median,ratings_average,ratings_count",
        "language": "eng",
    }
    try:
        resp = requests.get(OL_SEARCH, params=params, timeout=120)
        resp.raise_for_status()
        return resp.json().get("docs", [])
    except requests.RequestException as e:
        print(f"  ⚠ Search failed for '{query}': {e}")
        return []


def fetch_work_description(work_key):
    """Fetch description from Open Library Works API."""
    try:
        resp = requests.get(f"{OL_WORKS}{work_key}.json", timeout=15)
        resp.raise_for_status()
        data = resp.json()
        desc = data.get("description", "")
        return clean_description(desc)
    except requests.RequestException:
        return ""


def process_book(doc, works_cache):
    """Process an Open Library search result into a book record."""
    title = (doc.get("title") or "").strip()
    if not title or len(title) < 2:
        return None

    # Skip certain non-book entries
    lower_title = title.lower()
    skip_patterns = ["coloring book", "activity book", "workbook",
                     "study guide", "teacher's edition", "test bank",
                     "solutions manual", "instructor's manual"]
    if any(p in lower_title for p in skip_patterns):
        return None

    work_key = doc.get("key", "")
    if not work_key:
        return None

    author = ", ".join(doc.get("author_name", [])[:2]) if doc.get("author_name") else ""
    year = doc.get("first_publish_year", 0) or 0
    cover_i = doc.get("cover_i")
    cover_url = f"{OL_COVER_BASE}/{cover_i}-L.jpg" if cover_i else ""

    # Extract genres/subjects
    subjects = doc.get("subject", [])
    if subjects:
        # Take the most relevant subject tags (up to 5)
        good_subjects = []
        for s in subjects[:30]:
            s_lower = s.lower()
            # Skip overly generic or metadata subjects
            if any(skip in s_lower for skip in [
                "protected daisy", "accessible book", "internet archive",
                "in library", "overdrive", "nyt:", "large type",
                "reading level", "lexile", "fiction in english",
                "american fiction", "english fiction", "fiction",
            ]):
                continue
            if len(s) > 3 and len(s) < 40:
                good_subjects.append(s.title())
            if len(good_subjects) >= 5:
                break
        genre = ", ".join(good_subjects)
    else:
        genre = ""

    rating = doc.get("ratings_average")
    avg_rating = round(float(rating), 1) if rating else 0.0

    # Try to get description from Works API (cached)
    description = ""
    if work_key in works_cache:
        description = works_cache[work_key]
    else:
        description = fetch_work_description(work_key)
        works_cache[work_key] = description
        time.sleep(WORKS_DELAY)

    # If no description, build from metadata
    if not description or len(description) < 20:
        parts = []
        if title:
            parts.append(title)
        if author:
            parts.append(f"by {author}")
        if genre:
            parts.append(f"Subjects: {genre}")
        description = ". ".join(parts) if parts else ""

    if not description or len(description) < 10:
        return None

    return {
        "ol_key": work_key,
        "title": title,
        "author": author,
        "media_type": "book",
        "description": description,
        "genre": genre,
        "year": year,
        "avg_rating": avg_rating,
        "poster_url": cover_url,
        "cover_i": cover_i or 0,
    }


def main():
    print("=" * 60)
    print("StorySense — Fetch Real Books from Open Library")
    print("=" * 60)

    search_cache = load_json_cache(SEARCH_CACHE)
    works_cache = load_json_cache(WORKS_CACHE)

    seen_titles = set()  # For deduplication (title+author)
    all_books = []

    # Check for existing partial results
    if "books" in search_cache and len(search_cache["books"]) > 0:
        all_books = search_cache["books"]
        seen_titles = {(b["title"].lower(), b.get("author", "").lower()) for b in all_books}
        print(f"📦 Restored {len(all_books)} books from cache")

    target_total = 0  # Changed to 0 to save currently cached books (approx 1000)

    if len(all_books) < target_total:
        for query, subject_hint, target_count in SEARCH_QUERIES:
            if len(all_books) >= target_total:
                break

            cache_key = f"search:{query}"
            if cache_key in search_cache and cache_key != "books":
                docs = search_cache[cache_key]
                print(f"\n📚 [cached] '{query}' ({len(docs)} results)")
            else:
                print(f"\n📚 Searching: '{query}' (target: {target_count})...")
                docs = search_books(query, limit=100)
                search_cache[cache_key] = docs
                time.sleep(SEARCH_DELAY)

            added = 0
            for doc in docs:
                if added >= target_count or len(all_books) >= target_total:
                    break

                title_lower = (doc.get("title") or "").lower().strip()
                author_lower = ", ".join(doc.get("author_name", [])[:2]).lower()
                dedup_key = (title_lower, author_lower)

                if dedup_key in seen_titles:
                    continue

                book = process_book(doc, works_cache)
                if book:
                    all_books.append(book)
                    seen_titles.add(dedup_key)
                    added += 1

            print(f"  ✓ Added {added} books ({len(all_books)} total)")

            # Save caches periodically
            if len(all_books) % 100 < 30:
                search_cache["books"] = all_books
                save_json_cache(search_cache, SEARCH_CACHE)
                save_json_cache(works_cache, WORKS_CACHE)

    # Save final caches
    search_cache["books"] = all_books
    save_json_cache(search_cache, SEARCH_CACHE)
    save_json_cache(works_cache, WORKS_CACHE)

    # Deduplicate by title (case-insensitive)
    print(f"\n📊 Pre-dedup count: {len(all_books)}")
    deduped = {}
    for b in all_books:
        key = b["title"].lower().strip()
        if key not in deduped:
            deduped[key] = b
    books_list = list(deduped.values())

    # Prefer books with covers and descriptions, trim to 2000
    def sort_key(b):
        score = 0
        if b.get("poster_url"):
            score += 1000
        if b.get("description") and len(b["description"]) > 50:
            score += 500
        if b.get("avg_rating", 0) > 0:
            score += 100
        if b.get("year", 0) > 0:
            score += 50
        return score

    books_list.sort(key=sort_key, reverse=True)
    books_list = books_list[:2000]

    # Assign content IDs
    for i, b in enumerate(books_list):
        b["content_id"] = f"BK_{i+1:04d}"

    # Save to CSV
    df = pd.DataFrame(books_list)
    columns = ["content_id", "title", "author", "media_type", "description",
               "genre", "year", "avg_rating", "poster_url", "ol_key"]
    df[columns].to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_NONNUMERIC)

    # Stats
    with_cover = (df["poster_url"] != "").sum()
    with_desc = (df["description"].str.len() > 50).sum()
    with_author = (df["author"] != "").sum()

    print(f"\n{'=' * 60}")
    print(f"✓ Saved {len(df)} real books to {OUTPUT_CSV}")
    print(f"  With cover: {with_cover}")
    print(f"  With description (>50 chars): {with_desc}")
    print(f"  With author: {with_author}")
    print(f"  Year range: {df[df['year'] > 0]['year'].min()} – {df[df['year'] > 0]['year'].max()}")
    print(f"\n  Top genres:")
    genres = df["genre"].str.split(", ").explode().str.strip()
    genres = genres[genres != ""]
    for g, count in genres.value_counts().head(15).items():
        print(f"    {g}: {count}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
