#!/usr/bin/env python3
"""
prepare_dataset.py — Normalize movies_tv.csv and books.csv into a unified schema.

Unified schema:
  content_id | title | media_type | description | genre | year | rating

Usage:
    python prepare_dataset.py
"""

import os
import pandas as pd
import re


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "unified_dataset.csv")


def clean_text(text: str) -> str:
    """Basic text cleaning: strip HTML tags, normalize whitespace."""
    if pd.isna(text):
        return ""
    text = re.sub(r"<[^>]+>", "", str(text))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_movies(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={
        "overview": "description",
        "genres": "genre",
        "release_date": "year",
        "rating": "rating",
    })
    # Extract year from date
    df["year"] = pd.to_datetime(df["year"], errors="coerce").dt.year.fillna(0).astype(int)
    df["media_type"] = df["media_type"].str.lower()
    df["description"] = df["description"].apply(clean_text)
    df["genre"] = df["genre"].fillna("").str.replace(";", ", ", regex=False)
    df["avg_rating"] = df["rating"]
    return df[["content_id", "title", "media_type", "description", "genre", "year", "avg_rating"]]


def load_books(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={
        "description": "description",
        "genres": "genre",
        "publication_year": "year",
        "avg_rating": "rating",
    })
    df["media_type"] = "book"
    df["description"] = df["description"].apply(clean_text)
    df["genre"] = df["genre"].fillna("").str.replace(";", ", ", regex=False)
    df["avg_rating"] = df["rating"]
    return df[["content_id", "title", "media_type", "description", "genre", "year", "avg_rating"]]


def main():
    movies_path = os.path.join(DATA_DIR, "movies_tv.csv")
    books_path = os.path.join(DATA_DIR, "books.csv")

    print("Loading movies/TV data...")
    movies = load_movies(movies_path)
    print(f"  Loaded {len(movies)} movies/TV entries")

    print("Loading books data...")
    books = load_books(books_path)
    print(f"  Loaded {len(books)} books")

    unified = pd.concat([movies, books], ignore_index=True)
    unified.to_csv(OUTPUT_FILE, index=False)

    print(f"\nUnified dataset saved to {OUTPUT_FILE}")
    print(f"Total entries: {len(unified)}")
    print(f"Media type distribution:")
    print(f"  {unified['media_type'].value_counts().to_string()}")
    print(f"\nSchema: {list(unified.columns)}")


if __name__ == "__main__":
    main()
