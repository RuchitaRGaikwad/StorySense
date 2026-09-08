#!/usr/bin/env python3
"""
prepare_dataset.py — Merge movies_real.csv and books_real.csv into unified_dataset.csv.

Unified schema:
  content_id | title | media_type | description | genre | year | avg_rating | poster_url

Usage:
    python prepare_dataset.py
"""

import os
import re
import csv
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MOVIES_CSV = os.path.join(DATA_DIR, "movies_real.csv")
BOOKS_CSV = os.path.join(DATA_DIR, "books_real.csv")
MOVIES_TV_CSV = os.path.join(DATA_DIR, "movies_tv.csv")
BOOKSMORE_CSV = os.path.join(DATA_DIR, "booksmore.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "unified_dataset.csv")


def clean_text(text):
    """Basic text cleaning: strip HTML tags, normalize whitespace."""
    if pd.isna(text):
        return ""
    text = re.sub(r"<[^>]+>", "", str(text))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    print("=" * 60)
    print("StorySense — Prepare Unified Dataset")
    print("=" * 60)

    # Load movies
    if not os.path.exists(MOVIES_CSV):
        print(f"✗ {MOVIES_CSV} not found.")
        movies = pd.DataFrame()
    else:
        movies = pd.read_csv(MOVIES_CSV)
        print(f"  Loaded {len(movies)} movies from movies_real.csv")

    # Load books
    if not os.path.exists(BOOKS_CSV):
        print(f"✗ {BOOKS_CSV} not found.")
        books = pd.DataFrame()
    else:
        books = pd.read_csv(BOOKS_CSV)
        print(f"  Loaded {len(books)} books from books_real.csv")

    # Load extra movies/tv
    if not os.path.exists(MOVIES_TV_CSV):
        print(f"✗ {MOVIES_TV_CSV} not found.")
        movies_tv = pd.DataFrame()
    else:
        movies_tv = pd.read_csv(MOVIES_TV_CSV)
        print(f"  Loaded {len(movies_tv)} items from movies_tv.csv")

    # Load extra books
    if not os.path.exists(BOOKSMORE_CSV):
        print(f"✗ {BOOKSMORE_CSV} not found.")
        booksmore = pd.DataFrame()
    else:
        booksmore = pd.read_csv(BOOKSMORE_CSV)
        if "cover_url" in booksmore.columns and "poster_url" not in booksmore.columns:
            booksmore = booksmore.rename(columns={"cover_url": "poster_url"})
        print(f"  Loaded {len(booksmore)} books from booksmore.csv")

    # Normalize columns to unified schema
    unified_cols = ["content_id", "title", "media_type", "description",
                    "genre", "year", "avg_rating", "poster_url"]

    datasets = []
    
    if not movies.empty:
        movies_df = movies[unified_cols].copy()
        movies_df["description"] = movies_df["description"].apply(clean_text)
        datasets.append(movies_df)

    if not books.empty:
        books_df = books[unified_cols].copy()
        books_df["description"] = books_df["description"].apply(clean_text)
        datasets.append(books_df)
        
    if not movies_tv.empty:
        movies_tv_df = movies_tv[unified_cols].copy()
        movies_tv_df["description"] = movies_tv_df["description"].apply(clean_text)
        datasets.append(movies_tv_df)
        
    if not booksmore.empty:
        booksmore_df = booksmore[unified_cols].copy()
        booksmore_df["description"] = booksmore_df["description"].apply(clean_text)
        datasets.append(booksmore_df)

    # Merge
    if datasets:
        unified = pd.concat(datasets, ignore_index=True)
    else:
        print("No data to merge!")
        return

    # Fill NaN poster_url with empty string
    unified["poster_url"] = unified["poster_url"].fillna("")
    unified["genre"] = unified["genre"].fillna("")
    unified["description"] = unified["description"].fillna("")
    unified["year"] = unified["year"].fillna(0).astype(int)
    unified["avg_rating"] = unified["avg_rating"].fillna(0.0)

    # Regenerate unique content_ids to avoid collisions
    movie_counter = 1
    book_counter = 1
    tv_counter = 1
    
    new_ids = []
    for media_type in unified["media_type"]:
        mt = str(media_type).lower()
        if mt == "movie":
            new_ids.append(f"MOV_{movie_counter:04d}")
            movie_counter += 1
        elif mt == "book":
            new_ids.append(f"BK_{book_counter:04d}")
            book_counter += 1
        elif mt == "tv":
            new_ids.append(f"TV_{tv_counter:04d}")
            tv_counter += 1
        else:
            new_ids.append(f"UNK_{movie_counter:04d}")
            
    unified["content_id"] = new_ids

    # Validation
    print(f"\n  Validation:")
    dup_ids = unified["content_id"].duplicated().sum()
    print(f"    Duplicate content_ids: {dup_ids}")
    missing_desc = (unified["description"].str.len() < 10).sum()
    print(f"    Missing/short descriptions: {missing_desc}")
    missing_genre = (unified["genre"] == "").sum()
    print(f"    Missing genres: {missing_genre}")
    with_poster = (unified["poster_url"] != "").sum()
    print(f"    With poster/cover: {with_poster}/{len(unified)}")

    # Save
    unified.to_csv(OUTPUT_FILE, index=False, quoting=csv.QUOTE_NONNUMERIC)

    print(f"\n  Unified dataset saved to {OUTPUT_FILE}")
    print(f"  Total entries: {len(unified)}")
    print(f"  Media type distribution:")
    print(f"    {unified['media_type'].value_counts().to_string()}")
    print(f"  Schema: {list(unified.columns)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
