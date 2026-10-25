#!/usr/bin/env python3
"""
Zenith / FocusRedirect: Hybrid Local RAG Engine
Combines:
1. Personal Study & Project Context (active topics, course syllabi, research goals)
2. Channel & Creator Knowledge Base (verified educational creators, universities, podcasts)
3. Self-Learning Feedback Memory (few-shot exemplars from user history & manual overrides)

Designed for sub-5ms execution to augment Jev (so1) System-One neural decisions without latency penalty.
"""

import os
import re
import math
import time
import json
import sqlite3
import threading
from urllib.parse import urlparse

DB_PATH = os.path.join(os.path.dirname(__file__), "rag_memory.sqlite")

# --- INITIAL SEED KNOWLEDGE BASES ---

DEFAULT_CREATORS = [
    # Aerospace, CFD & Scientific Machine Learning
    {"name": "Steve Brunton", "aliases": ["steve brunton", "kutz", "data-driven science"], "category": "engineering_cfd", "type": "lecture", "trust": 1.0, "notes": "Data-driven dynamical systems, SVD, PINNs, and fluid mechanics"},
    {"name": "Fluid Toolbox", "aliases": ["fluid toolbox", "aidan wimshurst", "cfd ninja"], "category": "engineering_cfd", "type": "lecture", "trust": 0.98, "notes": "Practical aerodynamics, CFD meshing, compressible flow, and OpenFOAM"},
    {"name": "Jozsef Nagy", "aliases": ["jozsef nagy", "openfoam tutorial"], "category": "engineering_cfd", "type": "lecture", "trust": 0.98, "notes": "OpenFOAM CFD simulation, boundary layers, and turbulence modeling"},
    {"name": "NPTEL Aerospace Engineering", "aliases": ["nptel aerospace", "nptel fluid", "nptel cfd"], "category": "academic", "type": "lecture", "trust": 1.0, "notes": "University graduate lectures in aerodynamics, gas dynamics, and propulsion"},
    {"name": "AIAA Aviation & SciTech", "aliases": ["aiaa", "scitech", "aiaa aviation", "aiaa journal"], "category": "academic", "type": "lecture", "trust": 1.0, "notes": "AIAA aerospace technical conferences, flight mechanics, and papers"},
    {"name": "3Blue1Brown", "aliases": ["3blue1brown", "grant sanderson"], "category": "mathematics", "type": "lecture", "trust": 1.0, "notes": "Essence of Linear Algebra, Calculus, Neural Networks, Differential Equations"},
    {"name": "MIT OpenCourseWare", "aliases": ["mit opencourseware", "mit 18.06", "mit 16.00", "mit ocw"], "category": "academic", "type": "lecture", "trust": 1.0, "notes": "MIT Aerodynamics, Fluid Dynamics, and Applied Mathematics"},
    {"name": "Stanford Online", "aliases": ["stanford online", "aa210", "cs229", "stanford engineering"], "category": "academic", "type": "lecture", "trust": 1.0, "notes": "Stanford Aeronautics & Astronautics and Machine Learning Courses"},
    {"name": "Two Minute Papers", "aliases": ["two minute papers", "kÃ¡roly zsolnai-fehÃ©r"], "category": "ai_research", "type": "lecture", "trust": 0.95, "notes": "AI, physics simulation, neural operators, and computational fluids"},
    {"name": "StatQuest with Josh Starmer", "aliases": ["statquest", "josh starmer"], "category": "statistics_ml", "type": "lecture", "trust": 0.98, "notes": "Statistics, Neural Networks, PCA, Machine Learning"},
    {"name": "Andrej Karpathy", "aliases": ["andrej karpathy", "karpathy"], "category": "ai_research", "type": "lecture", "trust": 1.0, "notes": "Neural networks, backprop, and deep learning architectures from scratch"},
    {"name": "Yannic Kilcher", "aliases": ["yannic kilcher"], "category": "ai_research", "type": "lecture", "trust": 0.98, "notes": "Academic ML paper readings and neural architecture reviews"},
    {"name": "Veritasium", "aliases": ["veritasium", "derek muller"], "category": "physics_science", "type": "lecture", "trust": 0.95, "notes": "In-depth physics, fluid dynamics experiments, and engineering"},
    {"name": "Computerphile", "aliases": ["computerphile", "brady haran"], "category": "computer_science", "type": "lecture", "trust": 0.98, "notes": "Algorithms, floating-point arithmetic, and high-performance computing"},
    
    # High-Signal Podcasts & Long-form Scientific Interviews
    {"name": "Lex Fridman Podcast", "aliases": ["lex fridman", "fridman podcast"], "category": "podcast", "type": "podcast", "trust": 0.96, "notes": "Technical, aerospace, physics, and AI deep-dive conversations"},
    {"name": "Dwarkesh Patel", "aliases": ["dwarkesh patel", "dwarkesh podcast"], "category": "podcast", "type": "podcast", "trust": 0.98, "notes": "High-intellect interviews on AI, physics, semiconductors, and deep tech"},
    {"name": "Sean Carroll's Mindscape", "aliases": ["mindscape podcast", "sean carroll"], "category": "physics_philosophy", "type": "podcast", "trust": 0.97, "notes": "Theoretical physics, fluid dynamics, and dynamical systems"},
    {"name": "Huberman Lab", "aliases": ["huberman lab", "andrew huberman"], "category": "neuroscience", "type": "podcast", "trust": 0.94, "notes": "Stanford neuroscience, focus, physiology, and cognitive performance"},
    {"name": "Acquired Podcast", "aliases": ["acquired podcast", "acquired fm"], "category": "business_history", "type": "podcast", "trust": 0.98, "notes": "Definitive technical histories of aerospace and computing giants"}
]

DEFAULT_GOALS = [
    {
        "topic": "Aerodynamics & Computational Fluid Dynamics (CFD)",
        "keywords": ["aerodynamics", "cfd", "navier-stokes", "compressible", "boundary layer", "rans", "les", "mesh", "openfoam", "airfoil", "turbulent", "supersonic", "mach", "reynolds", "finite volume", "snappyhexminesh"],
        "category": "academic"
    },
    {
        "topic": "Physics-Informed Neural Networks (PINNs) & SciML",
        "keywords": ["physics-informed", "pinn", "sciml", "deepxde", "operator learning", "fno", "deeponet", "loss function", "autograd", "residual", "automatic differentiation", "neural operator"],
        "category": "academic"
    },
    {
        "topic": "Modal Decomposition, POD & Reduced Order Models (ROMs)",
        "keywords": ["proper orthogonal decomposition", "pod", "svd", "dmd", "dynamic mode decomposition", "reduced order model", "rom", "sindy", "brunton", "coherent structures", "singular value decomposition"],
        "category": "academic"
    },
    {
        "topic": "Turbulence Modeling & Data-Driven Closures (RANS/LES)",
        "keywords": ["turbulence", "reynolds stress", "boussinesq", "closure", "dns", "k-omega", "les", "subgrid-scale", "shear stress", "eddy viscosity", "anisotropy"],
        "category": "academic"
    },
    {
        "topic": "Aerospace Propulsion & Compressible Gas Dynamics",
        "keywords": ["propulsion", "gas turbine", "nozzle", "combustion", "rocketry", "thrust", "hypersonic", "shock wave", "flight mechanics", "compressor", "isentropic"],
        "category": "developer"
    },
    {
        "topic": "Aerospace Graduate Research & Journal Papers (AIAA/JFM)",
        "keywords": ["thesis", "jfm", "journal of fluid mechanics", "aiaa", "physics of fluids", "paper", "arxiv", "overleaf", "latex", "citations", "literature review", "methodology"],
        "category": "academic"
    }
]

DEFAULT_EXEMPLARS = [
    {"title": "Steve Brunton: Physics Informed Neural Networks (PINNs)", "domain": "youtube.com", "action": "ALLOW", "reason": "Engineering Research & Mathematical Physics", "profile": "academic"},
    {"title": "MIT 18.06 Linear Algebra, Spring 2005 - Gilbert Strang", "domain": "youtube.com", "action": "ALLOW", "reason": "Accredited University Course Lecture", "profile": "academic"},
    {"title": "Fluid Toolbox: How to Mesh Transonic Airfoils with SnappyHexMesh", "domain": "youtube.com", "action": "ALLOW", "reason": "Aerospace CFD Meshing Tutorial", "profile": "developer"},
    {"title": "Jozsef Nagy: OpenFOAM Turbulence Modeling and k-omega SST", "domain": "youtube.com", "action": "ALLOW", "reason": "CFD Numerical Simulation Lecture", "profile": "developer"},
    {"title": "AIAA SciTech: Fourier Neural Operators for Transonic Aerodynamic Surrogates", "domain": "youtube.com", "action": "ALLOW", "reason": "Aerospace Machine Learning Conference", "profile": "academic"},
    {"title": "DeepXDE Tutorial: Solving 2D Navier-Stokes Equations with PINNs", "domain": "youtube.com", "action": "ALLOW", "reason": "Scientific Machine Learning Deep Dive", "profile": "academic"},
    {"title": "Lex Fridman Podcast #400 - Jeff Bezos on Space and Rockets", "domain": "youtube.com", "action": "ALLOW", "reason": "Aerospace & Engineering Conversation", "profile": "general"},
    {"title": "Dwarkesh Patel: Demis Hassabis on Gemini, AlphaFold, and AGI", "domain": "youtube.com", "action": "ALLOW", "reason": "AI Research Leadership & Scientific Interview", "profile": "academic"},
    {"title": "Try Not To Laugh Challenge Compilation #42", "domain": "youtube.com", "action": "REDIRECT", "reason": "Casual Entertainment / Dopamine Trap", "profile": "general"},
    {"title": "I Spent 24 Hours in a Secret Underground Bunker", "domain": "youtube.com", "action": "REDIRECT", "reason": "High-dopamine Clickbait Entertainment", "profile": "general"},
    {"title": "GTA 6 - Official Gameplay Breakdown and Reactions", "domain": "youtube.com", "action": "REDIRECT", "reason": "Video Game Media & Speculation", "profile": "developer"},
    {"title": "Celebrity Drama Explained: Why Everyone is Unfollowing", "domain": "youtube.com", "action": "REDIRECT", "reason": "Gossip and Celebrity Distraction", "profile": "general"}
]


class LocalRAGService:
    def __init__(self):
        self._lock = threading.Lock()
        self._init_database()
        self._build_in_memory_index()
        self._last_retrieval_log = []

    def _init_database(self):
        """Initializes SQLite schema for local persistent RAG tables."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS creators_kb (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    aliases_json TEXT,
                    category TEXT,
                    type TEXT,
                    trust REAL,
                    notes TEXT,
                    created_at REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT UNIQUE,
                    keywords_json TEXT,
                    category TEXT,
                    created_at REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback_exemplars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    domain TEXT,
                    url TEXT,
                    action TEXT,
                    reason TEXT,
                    profile_id TEXT,
                    user_override INTEGER DEFAULT 0,
                    created_at REAL
                )
            """)
            conn.commit()

            # Seed if empty
            cursor.execute("SELECT COUNT(*) FROM creators_kb")
            if cursor.fetchone()[0] == 0:
                now = time.time()
                for c in DEFAULT_CREATORS:
                    cursor.execute("""
                        INSERT INTO creators_kb (name, aliases_json, category, type, trust, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (c["name"], json.dumps(c["aliases"]), c["category"], c["type"], c["trust"], c["notes"], now))
                conn.commit()

            cursor.execute("SELECT COUNT(*) FROM user_goals")
            if cursor.fetchone()[0] == 0:
                now = time.time()
                for g in DEFAULT_GOALS:
                    cursor.execute("""
                        INSERT INTO user_goals (topic, keywords_json, category, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (g["topic"], json.dumps(g["keywords"]), g["category"], now))
                conn.commit()

            cursor.execute("SELECT COUNT(*) FROM feedback_exemplars")
            if cursor.fetchone()[0] == 0:
                now = time.time()
                for ex in DEFAULT_EXEMPLARS:
                    cursor.execute("""
                        INSERT INTO feedback_exemplars (title, domain, url, action, reason, profile_id, user_override, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (ex["title"], ex["domain"], "", ex["action"], ex["reason"], ex.get("profile", "general"), 0, now))
                conn.commit()

    def _tokenize(self, text):
        """Ultra-fast regex tokenizer producing normalized n-grams & words."""
        if not text:
            return []
        text = text.lower()
        # Clean symbols
        clean = re.sub(r"[^\w\s]", " ", text)
        words = [w for w in clean.split() if len(w) > 1]
        return words

    def _build_in_memory_index(self):
        """Loads and indexes creators, goals, and exemplars in memory for < 2ms queries."""
        with self._lock:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Load creators
                cursor.execute("SELECT name, aliases_json, category, type, trust, notes FROM creators_kb")
                self.creators = []
                for row in cursor.fetchall():
                    aliases = json.loads(row["aliases_json"])
                    self.creators.append({
                        "name": row["name"],
                        "aliases": aliases,
                        "category": row["category"],
                        "type": row["type"],
                        "trust": row["trust"],
                        "notes": row["notes"]
                    })

                # Load goals
                cursor.execute("SELECT id, topic, keywords_json, category FROM user_goals")
                self.goals = []
                for row in cursor.fetchall():
                    kws = json.loads(row["keywords_json"])
                    self.goals.append({
                        "id": row["id"],
                        "topic": row["topic"],
                        "keywords": kws,
                        "category": row["category"],
                        "token_set": set(self._tokenize(row["topic"]) + [k.lower() for k in kws])
                    })

                # Load exemplars
                cursor.execute("SELECT id, title, domain, action, reason, profile_id, user_override FROM feedback_exemplars ORDER BY id DESC LIMIT 200")
                self.exemplars = []
                for row in cursor.fetchall():
                    tokens = set(self._tokenize(row["title"]))
                    self.exemplars.append({
                        "id": row["id"],
                        "title": row["title"],
                        "domain": row["domain"],
                        "action": row["action"],
                        "reason": row["reason"],
                        "profile_id": row["profile_id"],
                        "user_override": bool(row["user_override"]),
                        "token_set": tokens
                    })

    def retrieve(self, url, title, profile_id="academic", top_k=2):
        """
        Executes hybrid retrieval over:
        1. Creator / Channel Knowledge Base (exact alias / entity search)
        2. User Goals & Active Topics (Jaccard / TF-IDF semantic overlap)
        3. Self-Learning Feedback Exemplars (Few-shot learning memory)
        Returns structured context and an augmented prompt string for Jev.
        """
        start_t = time.perf_counter()
        title_clean = (title or "").strip()
        title_lower = title_clean.lower()
        title_tokens = set(self._tokenize(title_clean))

        # 1. Match Creators
        matched_creator = None
        for c in self.creators:
            for alias in c["aliases"]:
                if alias in title_lower or (url and alias in url.lower()):
                    matched_creator = c
                    break
            if matched_creator:
                break

        # 2. Match User Context Goals
        goal_matches = []
        for g in self.goals:
            # Check direct keyword occurrences in title
            kw_hits = [kw for kw in g["keywords"] if kw in title_lower]
            # Token overlap
            overlap = len(title_tokens & g["token_set"])
            if kw_hits or overlap > 0:
                score = (len(kw_hits) * 2.0 + overlap) / max(1, len(title_tokens))
                goal_matches.append({
                    "topic": g["topic"],
                    "category": g["category"],
                    "matched_keywords": kw_hits,
                    "score": round(min(1.0, score), 3)
                })

        goal_matches.sort(key=lambda x: x["score"], reverse=True)
        top_goals = goal_matches[:2]

        # 3. Retrieve Few-Shot Exemplars from Memory
        exemplar_scores = []
        for ex in self.exemplars:
            if not ex["token_set"]:
                continue
            common = len(title_tokens & ex["token_set"])
            if common > 0:
                # Bonus if domain matches
                domain_bonus = 0.5 if ex["domain"] in (url or "") else 0.0
                score = (common / len(title_tokens | ex["token_set"])) + domain_bonus
                if ex["user_override"]:
                    score += 0.3  # Prioritize user explicit overrides
                exemplar_scores.append((score, ex))

        exemplar_scores.sort(key=lambda x: x[0], reverse=True)
        top_exemplars = [ex for s, ex in exemplar_scores[:top_k]]

        # Construct Jev Augmented Prompt Context
        context_snippets = []
        if matched_creator:
            context_snippets.append(f"Creator: {matched_creator['name']} ({matched_creator['notes']})")

        if top_goals:
            goals_str = ", ".join([f"'{g['topic']}'" for g in top_goals])
            context_snippets.append(f"Aligned User Goals: {goals_str}")

        if top_exemplars:
            ex_str = " | ".join([f"Past '{e['title'][:28]}...' -> {e['action']}" for e in top_exemplars])
            context_snippets.append(f"Similar Past Exemplars: {ex_str}")

        rag_summary = " // ".join(context_snippets) if context_snippets else "No historical context match"
        latency_ms = round((time.perf_counter() - start_t) * 1000, 2)

        # Clean serializable exemplars (exclude set objects)
        serializable_exemplars = [
            {
                "id": ex["id"],
                "title": ex["title"],
                "domain": ex["domain"],
                "action": ex["action"],
                "reason": ex["reason"],
                "user_override": ex["user_override"]
            }
            for ex in top_exemplars
        ]

        result = {
            "has_context": bool(matched_creator or top_goals or top_exemplars),
            "matched_creator": matched_creator,
            "matched_goals": top_goals,
            "few_shot_exemplars": serializable_exemplars,
            "rag_summary": rag_summary,
            "retrieval_latency_ms": latency_ms
        }

        # Cache last retrieval for dashboard telemetry
        with self._lock:
            self._last_retrieval_log.insert(0, {
                "title": title_clean,
                "url": url,
                "matched_creator": matched_creator["name"] if matched_creator else None,
                "matched_goals": [g["topic"] for g in top_goals] if top_goals else [],
                "few_shot_count": len(serializable_exemplars),
                "summary": rag_summary,
                "latency_ms": latency_ms,
                "timestamp": time.strftime("%H:%M:%S")
            })
            if len(self._last_retrieval_log) > 10:
                self._last_retrieval_log.pop()

        return result

    def record_feedback(self, title, domain, action, reason, url="", user_override=True, profile_id="academic"):
        """Records a new decision or manual override into persistent memory."""
        now = time.time()
        with self._lock:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO feedback_exemplars (title, domain, url, action, reason, profile_id, user_override, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, domain, url, action, reason, profile_id, 1 if user_override else 0, now))
                conn.commit()

        # Refresh index in background
        self._build_in_memory_index()
        return {"status": "ok", "message": f"Learned exemplar: {title[:32]} -> {action}"}

    def add_user_goal(self, topic, keywords, category="academic"):
        """Adds a new study or project topic to the user's RAG knowledge store."""
        now = time.time()
        with self._lock:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_goals (topic, keywords_json, category, created_at)
                    VALUES (?, ?, ?, ?)
                """, (topic, json.dumps(keywords), category, now))
                conn.commit()

        self._build_in_memory_index()
        return {"status": "ok", "topic": topic}

    def delete_user_goal(self, goal_id):
        """Deletes a topic from user goals."""
        with self._lock:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_goals WHERE id = ?", (goal_id,))
                conn.commit()
        self._build_in_memory_index()
        return {"status": "ok"}

    def reset_to_aerospace_seeds(self):
        """Re-seeds goals and creators specifically for Aerospace & CFD / SciML."""
        with self._lock:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_goals")
                now = time.time()
                for g in DEFAULT_GOALS:
                    cursor.execute("""
                        INSERT INTO user_goals (topic, keywords_json, category, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (g["topic"], json.dumps(g["keywords"]), g["category"], now))

                cursor.execute("DELETE FROM creators_kb")
                for c in DEFAULT_CREATORS:
                    cursor.execute("""
                        INSERT INTO creators_kb (name, aliases_json, category, type, trust, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (c["name"], json.dumps(c["aliases"]), c["category"], c["type"], c["trust"], c["notes"], now))
                conn.commit()
        self._build_in_memory_index()
        return {"status": "ok", "goals_count": len(self.goals), "creators_count": len(self.creators)}

    def get_stats(self):
        """Returns statistics for dashboard telemetry."""
        return {
            "creators_indexed": len(self.creators),
            "user_goals": [
                {"id": g["id"], "topic": g["topic"], "category": g["category"]}
                for g in self.goals
            ],
            "exemplars_count": len(self.exemplars),
            "recent_retrievals": self._last_retrieval_log[:5]
        }


# Singleton RAG instance
_rag_instance = None
_rag_init_lock = threading.Lock()

def get_rag():
    global _rag_instance
    if _rag_instance is not None:
        return _rag_instance
    with _rag_init_lock:
        if _rag_instance is None:
            _rag_instance = LocalRAGService()
        return _rag_instance


if __name__ == "__main__":
    rag = get_rag()
    test_queries = [
        ("https://www.youtube.com/watch?v=1", "3Blue1Brown - Neural Networks: But what is a neural network?"),
        ("https://www.youtube.com/watch?v=2", "Steve Brunton: Physics-Informed Neural Networks for Fluid Mechanics"),
        ("https://www.youtube.com/watch?v=3", "Dwarkesh Patel - Demis Hassabis on DeepMind and Protein Folding"),
        ("https://www.youtube.com/watch?v=4", "Craziest TikTok Fails of the Week Compilation 2024"),
    ]

    print("=== Testing Zenith Local RAG Engine ===")
    for u, t in test_queries:
        res = rag.retrieve(u, t, profile_id="academic")
        print(f"\nTarget: {t}")
        print(f"Latency: {res['retrieval_latency_ms']}ms")
        print(f"Augmented Context: {res['rag_summary']}")
        if res["matched_creator"]:
            print(f"Verified Creator: {res['matched_creator']['name']} ({res['matched_creator']['trust']})")
        if res["matched_goals"]:
            print(f"Aligned Goals: {[g['topic'] for g in res['matched_goals']]}")
        if res["few_shot_exemplars"]:
            print(f"Exemplar Memory: {[e['title'][:25] for e in res['few_shot_exemplars']]}")
