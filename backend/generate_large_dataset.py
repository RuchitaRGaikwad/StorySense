#!/usr/bin/env python3
"""
generate_large_dataset.py — Generate expanded realistic sample datasets.

Creates ~2000 movies/TV entries and ~3000 book entries with realistic
titles, descriptions, genres, and metadata. Clearly labeled as sample data.

Usage:
    python generate_large_dataset.py
"""

import csv
import os
import random

random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ---------------------------------------------------------------------------
# GENRE / THEME POOLS
# ---------------------------------------------------------------------------

MOVIE_GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
    "Drama", "Family", "Fantasy", "History", "Horror", "Music", "Mystery",
    "Romance", "Science Fiction", "Thriller", "War", "Western",
]

TV_GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
    "Drama", "Family", "Fantasy", "History", "Horror", "Mystery",
    "Romance", "Sci-Fi", "Thriller", "War", "Western",
]

BOOK_GENRES = [
    "Fiction", "Non-Fiction", "Science Fiction", "Fantasy", "Mystery",
    "Thriller", "Romance", "Horror", "Historical", "Biography",
    "Self-Help", "Science", "Philosophy", "Adventure", "Drama",
    "Crime", "Dystopia", "Cyberpunk", "Young Adult", "Humor",
    "Psychology", "War", "Mythology", "Technology", "Engineering",
    "Memoir", "Poetry", "Religion", "Art", "Travel",
]

# Theme / setting building blocks for generating diverse descriptions
SETTINGS = [
    "a sprawling metropolis", "a remote mountain village", "a war-torn country",
    "a futuristic space station", "an ancient kingdom", "a quiet coastal town",
    "a mysterious island", "a dystopian wasteland", "the American Midwest",
    "1920s Paris", "Victorian London", "modern-day Tokyo", "a parallel universe",
    "the Australian outback", "a crumbling empire", "the Arctic tundra",
    "a dense tropical rainforest", "an orbiting colony ship", "the Sahara Desert",
    "a labyrinthine underground city", "a floating city in the clouds",
    "a small Appalachian town", "the streets of Mumbai", "a cyberpunk megacity",
    "a medieval castle", "a forbidden zone beyond the border",
    "post-apocalyptic Earth", "a secluded monastery", "a lunar mining base",
    "the canals of Venice", "an underwater research facility", "cold-war Berlin",
    "a haunted Victorian manor", "a thriving alien bazaar", "the Silk Road",
    "a digital simulation", "a war-weary frontier town", "a magical academy",
    "a government black site", "1960s New York", "a dying star system",
]

PROTAGONIST_TYPES = [
    "a disillusioned detective", "a young orphan", "a retired soldier",
    "a brilliant scientist", "a struggling artist", "a rogue hacker",
    "a reluctant heir", "an ambitious journalist", "a widowed teacher",
    "a former spy", "a ship captain", "a street-smart teenager",
    "an idealistic doctor", "a disgraced politician", "a gifted musician",
    "a cunning thief", "an alien diplomat", "a battle-scarred warrior",
    "a compassionate nurse", "a skeptical philosopher", "an astronaut",
    "a medieval knight", "a rebel leader", "a time-traveler",
    "a cursed sorcerer", "a clone searching for identity",
    "an AI gaining sentience", "a war correspondent", "a fugitive on the run",
    "a deep-sea explorer", "a vigilante seeking justice",
    "a grieving parent", "a shapeshifter", "a librarian with a secret",
    "a wandering monk", "a bounty hunter", "a tech billionaire",
    "a shipwrecked sailor", "a young prodigy", "a nomadic trader",
]

CONFLICTS = [
    "must unravel a conspiracy that threatens the entire nation",
    "is drawn into a web of intrigue after a mysterious murder",
    "discovers a hidden power that could change the course of history",
    "fights to survive in a world where trust is a luxury",
    "confronts a dark secret from their past that resurfaces violently",
    "races against time to prevent a catastrophic event",
    "navigates a treacherous political landscape while hiding a dangerous truth",
    "uncovers evidence of an alien intelligence watching humanity",
    "must choose between personal redemption and the greater good",
    "leads a ragged group of survivors through hostile territory",
    "faces an impossible moral dilemma that will define their legacy",
    "is forced to ally with an old enemy to defeat a common threat",
    "struggles to hold together a fractured community on the brink of collapse",
    "discovers that the reality they know is a carefully constructed illusion",
    "must decode an ancient prophecy before it's too late",
    "battles inner demons while fighting an external war",
    "is tasked with protecting a child who holds the key to survival",
    "infiltrates a powerful organization to expose corruption from within",
    "embarks on a perilous journey across uncharted lands",
    "grapples with the ethical implications of a groundbreaking discovery",
    "must broker peace between warring factions before all-out war erupts",
    "stumbles upon a portal to another dimension and must find a way home",
    "seeks revenge against the people who destroyed everything they loved",
    "awakens with no memory in a place that defies explanation",
    "is hunted by a relentless pursuer across multiple continents",
    "uncovers a centuries-old mystery buried beneath the city",
    "must lead humanity's last stand against an overwhelming enemy",
    "finds an artifact that grants extraordinary abilities at a terrible cost",
    "wrestles with the consequences of a decision that altered the timeline",
    "tries to save a dying world using forbidden knowledge",
]

THEMES_EXTRA = [
    "Along the way, themes of loyalty, sacrifice, and the meaning of home emerge.",
    "The story explores identity, belonging, and what it means to be human.",
    "At its heart, it is a meditation on grief, memory, and letting go.",
    "Questions of power, ethics, and the cost of progress run through every chapter.",
    "The narrative weaves together love, loss, and the resilience of the human spirit.",
    "It is both a gripping thriller and a poignant examination of family bonds.",
    "Tensions between tradition and innovation drive the characters apart—and together.",
    "The tale is infused with dark humor and sharp social commentary.",
    "Beneath the action lies a thoughtful reflection on freedom and responsibility.",
    "The story ultimately asks: how far would you go to protect what you love?",
    "Cultural clashes and unexpected alliances shape the path forward.",
    "A searing look at justice and vengeance in a morally ambiguous world.",
    "With lyrical prose, the narrative captures the beauty and brutality of nature.",
    "Technology and humanity collide in ways neither side can predict.",
    "It is a coming-of-age story wrapped in a larger epic of survival.",
]

# Title word pools for procedural title generation
TITLE_ADJ = [
    "Silent", "Crimson", "Broken", "Eternal", "Hidden", "Frozen", "Burning",
    "Shattered", "Forgotten", "Twisted", "Sacred", "Wicked", "Lost", "Golden",
    "Iron", "Silver", "Shadow", "Dark", "Bright", "Final", "Hollow",
    "Restless", "Fallen", "Pale", "Savage", "Midnight", "Amber", "Obsidian",
    "Crystal", "Emerald", "Sapphire", "Starlit", "Sunken", "Rising", "Endless",
    "Haunted", "Distant", "Ancient", "Rogue", "Fading", "Electric", "Phantom",
    "Velvet", "Ruthless", "Lethal", "Wandering", "Ashen", "Serene", "Luminous",
]

TITLE_NOUN = [
    "Empire", "Kingdom", "Legacy", "Horizon", "Labyrinth", "Abyss", "Storm",
    "Witness", "Chronicles", "Reckoning", "Covenant", "Cipher", "Threshold",
    "Requiem", "Dominion", "Verdict", "Eclipse", "Paradox", "Signal", "Fragment",
    "Meridian", "Vanguard", "Solstice", "Reverie", "Tempest", "Nexus",
    "Catalyst", "Pinnacle", "Descent", "Odyssey", "Inferno", "Haven",
    "Frontier", "Bastion", "Mirage", "Vertex", "Remnant", "Archive",
    "Passage", "Summit", "Rift", "Crucible", "Tribunal", "Monolith", "Oasis",
    "Sanctum", "Convergence", "Resonance", "Doctrine", "Forge",
]

TITLE_PATTERN_THE_NOUN = [
    "The {noun}", "The {adj} {noun}", "The Last {noun}",
    "The {noun} of {noun2}", "The {adj} {noun} of {noun2}",
]

TITLE_PATTERN_SIMPLE = [
    "{adj} {noun}", "{noun}", "{noun}: {adj} {noun2}",
    "Beyond the {noun}", "Into the {noun}", "Before the {noun}",
    "After the {noun}", "Beneath the {noun}", "Edge of {noun}",
    "Song of {noun}", "Children of the {noun}", "House of {noun}",
    "City of {adj} {noun}", "Order of the {noun}", "Path of {noun}",
    "Heart of {noun}", "Echoes of {noun}", "Shadows of {noun}",
    "Blood and {noun}", "Fire and {noun}", "Sword of {noun}",
    "{noun} Rising", "{noun} Falling", "Project {noun}",
    "Operation {noun}", "Protocol {noun}", "Code {noun}",
]

LANGUAGES = ["en"] * 85 + ["es"] * 3 + ["fr"] * 2 + ["de"] * 2 + ["ja"] * 2 + ["ko"] * 2 + ["zh"] * 1 + ["hi"] * 1 + ["it"] * 1 + ["pt"] * 1

BOOK_AUTHORS_FIRST = [
    "James", "Sarah", "Michael", "Elena", "David", "Maria", "Robert",
    "Aisha", "John", "Wei", "Thomas", "Yuki", "Daniel", "Priya",
    "William", "Sofia", "Mark", "Fatima", "Andrew", "Lena", "Paul",
    "Nadia", "Stephen", "Ingrid", "Peter", "Mei", "Charles", "Olga",
    "Richard", "Amara", "George", "Hana", "Edward", "Zara", "Joseph",
    "Leila", "Benjamin", "Anya", "Christopher", "Linh", "Matthew",
    "Suki", "Alexander", "Isla", "Nicholas", "Mira", "Anthony", "Freya",
    "Joshua", "Keiko",
]

BOOK_AUTHORS_LAST = [
    "Morrison", "Chen", "Williams", "Petrov", "García", "Nakamura",
    "Thompson", "Khan", "Anderson", "Müller", "Campbell", "Yamamoto",
    "Robinson", "Singh", "Walker", "Fernandez", "Mitchell", "Park",
    "Phillips", "Johansson", "Carter", "Volkov", "Sullivan", "Tanaka",
    "Brooks", "Ali", "Bennett", "Ivanova", "Foster", "Kim",
    "Howard", "Okafor", "Reed", "Larsson", "Cooper", "Suzuki",
    "Barnes", "Novak", "Price", "Reeves", "Hart", "Diaz",
    "Grant", "Kowalski", "Hayes", "Schmidt", "Murray", "Takahashi",
    "Graham", "Lindqvist",
]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

_used_titles: set[str] = set()


def _gen_title() -> str:
    """Generate a unique procedural title."""
    for _ in range(200):
        patterns = TITLE_PATTERN_THE_NOUN + TITLE_PATTERN_SIMPLE
        pat = random.choice(patterns)
        adj = random.choice(TITLE_ADJ)
        noun = random.choice(TITLE_NOUN)
        noun2 = random.choice(TITLE_NOUN)
        while noun2 == noun:
            noun2 = random.choice(TITLE_NOUN)
        title = pat.format(adj=adj, noun=noun, noun2=noun2)
        if title not in _used_titles:
            _used_titles.add(title)
            return title
    # Fallback: add a number
    base = f"{random.choice(TITLE_ADJ)} {random.choice(TITLE_NOUN)}"
    title = f"{base} {random.randint(2, 99)}"
    _used_titles.add(title)
    return title


def _gen_description() -> str:
    """Generate a realistic plot description."""
    setting = random.choice(SETTINGS)
    protagonist = random.choice(PROTAGONIST_TYPES)
    conflict = random.choice(CONFLICTS)
    extra = random.choice(THEMES_EXTRA)
    return f"Set in {setting}, {protagonist} {conflict}. {extra}"


def _pick_genres(pool: list[str], min_g: int = 1, max_g: int = 3) -> str:
    n = random.randint(min_g, max_g)
    return ";".join(random.sample(pool, min(n, len(pool))))


def _gen_date(start_year: int, end_year: int) -> str:
    y = random.randint(start_year, end_year)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    return f"{y}-{m:02d}-{d:02d}"


def _gen_rating(low: float = 5.0, high: float = 9.5) -> float:
    return round(random.uniform(low, high), 1)


def _gen_popularity() -> float:
    return round(random.uniform(10, 99), 1)


# ---------------------------------------------------------------------------
# KEEP EXISTING ROWS — load the originals and prepend them
# ---------------------------------------------------------------------------

def _load_existing_csv(path: str) -> list[dict]:
    """Load existing CSV rows if the file exists."""
    if not os.path.exists(path):
        return []
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# GENERATE MOVIES/TV
# ---------------------------------------------------------------------------

def generate_movies_tv(target_count: int = 2000) -> None:
    path = os.path.join(DATA_DIR, "movies_tv.csv")
    existing = _load_existing_csv(path)
    for row in existing:
        _used_titles.add(row["title"])

    fieldnames = [
        "content_id", "title", "media_type", "overview", "genres",
        "release_date", "rating", "popularity", "language",
    ]

    rows = list(existing)  # keep originals
    next_mov = len([r for r in existing if r.get("media_type", "").lower() == "movie"]) + 1
    next_tv = len([r for r in existing if r.get("media_type", "").lower() == "tv"]) + 1

    while len(rows) < target_count:
        is_movie = random.random() < 0.55  # slight movie bias
        if is_movie:
            cid = f"MOV{next_mov:04d}"
            next_mov += 1
            mtype = "Movie"
            genres = _pick_genres(MOVIE_GENRES)
            year_start, year_end = 1960, 2025
        else:
            cid = f"TV{next_tv:04d}"
            next_tv += 1
            mtype = "TV"
            genres = _pick_genres(TV_GENRES)
            year_start, year_end = 1990, 2025

        rows.append({
            "content_id": cid,
            "title": _gen_title(),
            "media_type": mtype,
            "overview": _gen_description(),
            "genres": genres,
            "release_date": _gen_date(year_start, year_end),
            "rating": str(_gen_rating(5.5, 9.2)),
            "popularity": str(_gen_popularity()),
            "language": random.choice(LANGUAGES),
        })

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    n_mov = sum(1 for r in rows if r["media_type"].lower() == "movie")
    n_tv = sum(1 for r in rows if r["media_type"].lower() == "tv")
    print(f"  movies_tv.csv: {len(rows)} rows ({n_mov} movies, {n_tv} TV)")


# ---------------------------------------------------------------------------
# GENERATE BOOKS
# ---------------------------------------------------------------------------

def generate_books(target_count: int = 3000) -> None:
    path = os.path.join(DATA_DIR, "books.csv")
    existing = _load_existing_csv(path)
    for row in existing:
        _used_titles.add(row["title"])

    fieldnames = [
        "content_id", "title", "media_type", "description", "authors",
        "genres", "publication_year", "avg_rating", "ratings_count",
    ]

    rows = list(existing)
    next_bk = len(existing) + 1

    while len(rows) < target_count:
        cid = f"BK{next_bk:04d}"
        next_bk += 1

        author = f"{random.choice(BOOK_AUTHORS_FIRST)} {random.choice(BOOK_AUTHORS_LAST)}"

        rows.append({
            "content_id": cid,
            "title": _gen_title(),
            "media_type": "Book",
            "description": _gen_description(),
            "authors": author,
            "genres": _pick_genres(BOOK_GENRES),
            "publication_year": str(random.randint(1920, 2025)),
            "avg_rating": str(_gen_rating(3.2, 4.8)),
            "ratings_count": str(random.randint(5000, 3500000)),
        })

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"  books.csv: {len(rows)} rows")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    print("Generating expanded datasets (sample data for prototype)...")
    generate_movies_tv(2000)
    generate_books(3000)
    print("Done! Datasets generated in", DATA_DIR)
    print("\nNext steps:")
    print("  1. python prepare_dataset.py")
    print("  2. python embed.py")


if __name__ == "__main__":
    main()
