#!/usr/bin/env python3
"""
embed.py — Precompute sentence embeddings for the unified dataset.

Uses all-MiniLM-L6-v2 from sentence-transformers.
Saves embeddings as .npy and content_ids as .json for fast lookup.

Usage:
    python embed.py
"""

import os
import json
import re
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
UNIFIED_CSV = os.path.join(DATA_DIR, "unified_dataset.csv")
EMBEDDINGS_FILE = os.path.join(DATA_DIR, "embeddings.npy")
IDS_FILE = os.path.join(DATA_DIR, "content_ids.json")

MODEL_NAME = "all-MiniLM-L6-v2"

# Download NLTK data (only needed once)
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)
try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet", quiet=True)


def preprocess_text(text: str) -> str:
    """
    Preprocess text: lowercase, strip punctuation, remove stopwords, lemmatize.
    """
    if not text or pd.isna(text):
        return ""

    # Lowercase
    text = text.lower()

    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Remove special characters and numbers (keep spaces)
    text = re.sub(r"[^a-z\s]", " ", text)

    # Tokenize
    tokens = text.split()

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]

    return " ".join(tokens)


def build_text_field(row: pd.Series) -> str:
    """
    Combine title + description + genre into a single text field for embedding.
    """
    parts = []
    if row.get("title"):
        parts.append(f"title: {row['title']}")
    if row.get("description"):
        parts.append(f"description: {row['description']}")
    if row.get("genre"):
        parts.append(f"genre: {row['genre']}")
    return " ".join(parts)


def main():
    print(f"Loading unified dataset from {UNIFIED_CSV}...")
    df = pd.read_csv(UNIFIED_CSV)
    print(f"  {len(df)} items loaded")

    # Build combined text fields
    print("Building combined text fields...")
    df["combined_text"] = df.apply(build_text_field, axis=1)

    # Preprocess
    print("Preprocessing text (lowercase, stopwords, lemmatization)...")
    df["processed_text"] = df["combined_text"].apply(preprocess_text)

    # Show sample
    print("\nSample processed text:")
    for _, row in df.head(3).iterrows():
        print(f"  [{row['content_id']}] {row['processed_text'][:120]}...")

    # Load model
    print(f"\nLoading sentence transformer model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    # Encode
    print("Encoding all items...")
    embeddings = model.encode(
        df["processed_text"].tolist(),
        show_progress_bar=True,
        batch_size=32,
        convert_to_numpy=True,
    )
    print(f"  Embeddings shape: {embeddings.shape}")

    # Save
    np.save(EMBEDDINGS_FILE, embeddings)
    content_ids = df["content_id"].tolist()
    with open(IDS_FILE, "w") as f:
        json.dump(content_ids, f)

    print(f"\nEmbeddings saved to {EMBEDDINGS_FILE}")
    print(f"Content IDs saved to {IDS_FILE}")
    print("Done!")


if __name__ == "__main__":
    main()
