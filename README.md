# StorySense — Cross-Media NLP Recommendation Engine

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SentenceTransformers](https://img.shields.io/badge/Model-all--MiniLM--L6--v2-FF6F00?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-v4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

> **StorySense** is a full-stack NLP recommendation engine that connects **movies**, **books**, and **TV series** based on the semantic similarity of their narrative plot descriptions. Powered by Sentence Transformers (`all-MiniLM-L6-v2`), vector embedding spaces, and cosine similarity distance.

---

## ✨ Features

- **Real NLP Pipeline**: Full text preprocessing (HTML stripping, stopword removal, WordNet lemmatization), 384-dimensional dense vector embeddings, and real-time cosine similarity.
- **Cross-Media Recommendations**: Discover books that match a movie's theme, or TV series connected to a novel — breaking down traditional media silos.
- **Zero Hardcoded Scores**: Every similarity percentage, top-N match, and evaluation score is computed live from high-dimensional vector space.
- **Editorial UI**: Human-designed, warm editorial aesthetic using a warm ivory background (`#F7F3EA`), deep forest green typography (`#1F3A32`), and subtle terracotta accents (`#B85C38`).
- **Interactive Evaluation Suite**: Real-time evaluation endpoint (`/api/evaluate`) computing Top-1/Top-5 similarity distributions and response latencies across the loaded dataset.
- **One-Click VS Code Launch**: Built-in `.vscode/tasks.json` configuration to boot both the FastAPI backend and React frontend simultaneously with `⇧⌘B`.

---

## 🛠 Tech Stack

### Backend
- **Framework**: Python 3.11+, FastAPI, Uvicorn
- **NLP & Vectors**: `sentence-transformers` (`all-MiniLM-L6-v2`), PyTorch, Hugging Face
- **Preprocessing**: NLTK (Stopwords, WordNet Lemmatizer), Regular Expressions
- **Similarity Computation**: `scikit-learn` (`cosine_similarity`), NumPy, Pandas

### Frontend
- **Framework**: React 19, Vite
- **Styling**: Tailwind CSS v4, Custom Design Tokens
- **Typography**: Newsreader (Editorial Serif) & Inter (Sans-Serif)
- **Routing**: React Router v7

---

## 📁 Project Structure

```
storysense/
├── .vscode/
│   └── tasks.json               # One-click VS Code launcher (⇧⌘B)
├── backend/
│   ├── main.py                  # FastAPI server & REST endpoints
│   ├── recommend.py             # Recommendation Engine & Cosine Similarity logic
│   ├── embed.py                 # NLTK preprocessing & Sentence Transformer encoder
│   ├── prepare_dataset.py       # Dataset normalization into unified schema
│   ├── generate_large_dataset.py # Expanded sample dataset generator (5,000 rows)
│   ├── requirements.txt         # Backend Python dependencies
│   └── data/
│       ├── movies_tv.csv        # Movies & TV series dataset (2,000 entries)
│       └── books.csv            # Books dataset (3,000 entries)
├── frontend/
│   ├── index.html               # Entry HTML & Google Font imports
│   ├── vite.config.js           # Vite dev server & /api proxy setup
│   ├── package.json             # Frontend dependencies
│   └── src/
│       ├── main.jsx             # React entry point
│       ├── App.jsx              # App layout, header, footer & router
│       ├── index.css            # Tailwind theme tokens & global styles
│       ├── App.css              # Animation keyframes & utility classes
│       └── pages/
│           ├── Home.jsx         # Search, autocomplete & media filters
│           ├── ItemDetail.jsx   # Source item card, recommendations grid & controls
│           ├── HowItWorks.jsx   # Interactive SVG pipeline diagram & step-by-step
│           └── Evaluation.jsx   # Live dataset metrics & latency evaluation
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### ⚡ Option A: One-Click Launch in VS Code (Recommended)

If you are using **VS Code**:

1. Open the project root folder in VS Code.
2. Press **`Shift + Command + B`** (`⇧⌘B` on macOS) or **`Ctrl + Shift + B`** on Windows/Linux.
3. VS Code will automatically set up the virtual environment, install dependencies, compute embeddings if missing, and launch both backend (`localhost:8000`) and frontend (`localhost:5173`).

---

### 🛠 Option B: Manual Terminal Setup

#### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Generate expanded sample dataset (5,000 rows)
python generate_large_dataset.py

# Prepare unified dataset
python prepare_dataset.py

# Precompute embeddings (downloads model on first run, ~1-3 min)
python embed.py

# Start FastAPI backend server
uvicorn main:app --reload --port 8000
```

The API will run at `http://localhost:8000`. Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

#### 2. Frontend Setup

```bash
# Open a new terminal and navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🔬 How It Works

```
┌─────────────────┐      ┌───────────────────┐      ┌────────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│ Raw Story Text  │ ───► │ NLP Preprocessing │ ───► │ Vector Embedding   │ ───► │ Cosine Distance  │ ───► │ Ranked Matches  │
│ Title+Plot+Genre│      │ NLTK Lemmatization│      │ MiniLM-L6 (384-dim)│      │ Dot Product Norm │      │ Cross-Media Top-N│
└─────────────────┘      └───────────────────┘      └────────────────────┘      └──────────────────┘      └─────────────────┘
```

1. **Normalization**: `prepare_dataset.py` unifies raw metadata from `movies_tv.csv` and `books.csv` into a standardized schema (`content_id`, `title`, `media_type`, `description`, `genre`, `year`, `rating`).
2. **Text Cleaning**: `embed.py` strips HTML tags, removes special characters, filters out English stopwords via NLTK, and applies WordNet lemmatization.
3. **Dense Encoding**: The combined `title + description + genre` text is encoded into 384-dimensional vector embeddings using `all-MiniLM-L6-v2`. Embeddings are cached to `embeddings.npy` for instant query lookup.
4. **Similarity Distance**: When querying an item, `recommend.py` calculates the cosine similarity angle between the target embedding vector and all candidate items:
   $$\text{cosine\_similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$
5. **Cross-Media Ranking**: Candidates are filtered by media type (cross-media by default), sorted by score, and returned with auto-generated contextual explanation keywords.

---

## 📊 API Endpoint Reference

| Method | Endpoint | Query Parameters | Description |
|--------|----------|------------------|-------------|
| `GET` | `/api/health` | — | API status and service health check |
| `GET` | `/api/content` | `query`, `media_type`, `limit` | Full-text title/plot search & autocomplete |
| `GET` | `/api/content/{id}` | — | Get single item details by `content_id` |
| `GET` | `/api/recommend/{id}` | `top_n`, `include_same_media`, `target_media` | Compute real cosine similarity recommendations |
| `GET` | `/api/evaluate` | — | Live dataset evaluation stats & query performance |

---

## 📝 Dataset & Provenance Note

> **Note on Dataset Scope**
>
> The project dataset combines hand-crafted entries of popular titles (*Inception, Dune, Stranger Things, Interstellar, 1984, Breaking Bad, etc.*) with realistic procedurally generated sample entries to demonstrate scalability up to **5,000 items** (2,000 Movies & TV shows, 3,000 Books).
> 
> All generated rows utilize authentic genre pairings and descriptive story arcs to ensure genuine semantic vector clustering.

---

## 📄 License

Distributed under the MIT License. Feel free to use and adapt for academic mini-projects, research, or portfolio demonstrations.
