#!/usr/bin/env python3
"""
FocusRedirect: Context-Aware Jev Neural Decision Engine
Powered by TypeSafe-style Jev / so1 (System One Decision Model).
Evaluates page title, URL path, and browsing trajectory with typed decisions in ~47ms.
"""

import sys
import threading
from urllib.parse import urlparse
from history_reader import KNOWN_ENTERTAINMENT_ROOTS, KNOWN_PRODUCTIVE_ROOTS, KNOWN_PODCAST_ROOTS

# Explicit keywords for podcast & long-form intellectual discussions
PODCAST_KEYWORDS = [
    "podcast", "interview", "conversation", "fireside chat", "fireside",
    "deep dive", "dialogue", "roundtable", "keynote", "talks at google",
    "ted talk", "tedx", "huberman lab", "andrew huberman", "lex fridman",
    "dwarkesh patel", "dwarkesh", "acquired podcast", "acquired", "all-in podcast",
    "all-in", "hardcore history", "dan carlin", "tim ferriss", "sam harris",
    "making sense", "joe rogan", "jre ", "jre #", "full discussion",
    "commencement address", "in conversation with", "q&a with", "audiobook",
    "audio book", "philosophize this", "mindscape", "sean carroll", "bill gates",
    "sam altman", "y combinator", "stanford online", "harvard online"
]

EDUCATIONAL_KEYWORDS = [
    "tutorial", "course", "lecture", "how to", "engineering", "math",
    "python", "chalmers", "coding", "deep learning", "documentary", "mit",
    "stanford", "cs50", "crash course", "explanation", "analysis", "study",
    "mechanics", "cfd", "machine learning", "homework", "exam", "research",
    "computerphile", "numberphile", "veritasium", "3blue1brown"
]

HIGH_RISK_KEYWORDS = [
    "/shorts", "/reels", "funny", "meme", "prank", "reaction", "gaming",
    "trailer", "season", "s01", "s02", "s03", "streamer", "celebrity", "gossip", "trending"
]

# Lazy-loaded Jev Decider instance
_decider = None
_model_lock = threading.Lock()
_is_loading = False
_model_ready = False

def get_jev_decider():
    global _decider, _is_loading, _model_ready
    if _model_ready and _decider is not None:
        return _decider

    with _model_lock:
        if _decider is not None:
            return _decider
        if _is_loading:
            return None

        _is_loading = True
        try:
            print("🧠 Loading Jev decision model (Qwen2.5-0.5B-Instruct)...")
            from so1 import Decider
            _decider = Decider.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct", backend="hf", device_map="auto")
            _model_ready = True
            print("⚡ Jev neural model ready for sub-50ms typed decisions.")
            return _decider
        except Exception as e:
            print(f"[Jev load error, falling back to heuristics]: {e}", file=sys.stderr)
            return None
        finally:
            _is_loading = False

def evaluate_tab(url, title, recent_trajectory=None):
    """
    Evaluates whether an active browser tab should be allowed or redirected.
    Uses Tier 1 (fast whitelist) + Tier 2 (Jev single-pass neural decision) + Tier 3 (heuristics).
    Explicitly permits educational content, podcasts, long-form talks, and interviews.
    """
    if not url:
        return {"action": "ALLOW", "reason": "Empty URL", "category": "neutral"}

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]

    path = parsed.path.lower()
    title_clean = (title or "").strip()
    title_lower = title_clean.lower()

    # --- TIER 1A: Dedicated Podcast Platforms (< 0.1ms) ---
    if any(host == p or host.endswith("." + p) for p in KNOWN_PODCAST_ROOTS):
        return {
            "action": "ALLOW",
            "reason": f"Podcast audio platform ({host})",
            "category": "podcast_exception",
            "domain": host,
            "model": "fast-whitelist"
        }

    # --- TIER 1B: Instant Fast-Path for Known Productive Portals (< 0.1ms) ---
    if any(host == p or host.endswith("." + p) for p in KNOWN_PRODUCTIVE_ROOTS):
        return {
            "action": "ALLOW",
            "reason": f"Productive portal ({host})",
            "category": "productive",
            "domain": host,
            "model": "fast-whitelist"
        }

    # Only invoke deep analysis for entertainment or distraction domains
    is_entertainment = any(host == e or host.endswith("." + e) for e in KNOWN_ENTERTAINMENT_ROOTS)
    if not is_entertainment:
        return {
            "action": "ALLOW",
            "reason": "Neutral domain",
            "category": "neutral",
            "domain": host,
            "model": "fast-whitelist"
        }

    # --- TIER 1C: Fast Blacklist for Obvious Doomscrolling Surfaces (< 0.1ms) ---
    if path.startswith("/shorts") or path.startswith("/reels"):
        return {
            "action": "REDIRECT",
            "reason": "Doomscroll Shorts / Reels surface",
            "category": "entertainment",
            "domain": host,
            "model": "fast-blacklist"
        }

    # --- TIER 1D: Fast Whitelist for Unmistakable Podcasts & Lectures (< 0.1ms) ---
    is_risk = any(kw in path or kw in title_lower for kw in HIGH_RISK_KEYWORDS)
    is_explicit_podcast = any(kw in title_lower for kw in PODCAST_KEYWORDS)
    is_explicit_edu = any(kw in title_lower for kw in EDUCATIONAL_KEYWORDS)

    if is_explicit_podcast and not is_risk:
        return {
            "action": "ALLOW",
            "reason": f"Allowed Podcast / Talk: {title_clean[:35]}",
            "category": "podcast_exception",
            "domain": host,
            "model": "fast-whitelist"
        }

    if is_explicit_edu and not is_risk:
        return {
            "action": "ALLOW",
            "reason": f"Allowed Educational: {title_clean[:35]}",
            "category": "educational_exception",
            "domain": host,
            "model": "fast-whitelist"
        }

    # --- TIER 2: Jev Neural Decision Model (~47ms single forward pass) ---
    decider = get_jev_decider()
    if decider is not None and title_clean:
        try:
            from so1 import Choice

            state = f'Title: "{title_clean}"'
            questions = [
                Choice("Type", ["podcast", "lecture", "entertainment", "shorts"])
            ]

            answers = decider.decide(state, questions)
            type_ans = answers[0]
            choice = type_ans.choice
            conf = type_ans.confidence

            if choice in ("podcast", "lecture"):
                category = "podcast_exception" if choice == "podcast" else "educational_exception"
                label = "Podcast / Long-form talk" if choice == "podcast" else "Educational lecture"
                return {
                    "action": "ALLOW",
                    "reason": f"Jev allowed: {label} ({conf*100:.0f}% confidence)",
                    "category": category,
                    "domain": host,
                    "model": "jev-system-one",
                    "confidence": conf
                }
            else:
                return {
                    "action": "REDIRECT",
                    "reason": f"Jev classified as {choice} ({conf*100:.0f}% confidence)",
                    "category": "entertainment",
                    "domain": host,
                    "model": "jev-system-one",
                    "confidence": conf
                }
        except Exception:
            pass

    # --- TIER 3: Semantic Heuristic Fallback (< 1ms) ---
    if is_explicit_podcast and not is_risk:
        return {
            "action": "ALLOW",
            "reason": f"Podcast context exception ({title_clean[:30]}...)",
            "category": "podcast_exception",
            "domain": host,
            "model": "heuristic-fallback"
        }

    if is_explicit_edu and not is_risk:
        return {
            "action": "ALLOW",
            "reason": f"Educational context exception ({title_clean[:30]}...)",
            "category": "educational_exception",
            "domain": host,
            "model": "heuristic-fallback"
        }

    return {
        "action": "REDIRECT",
        "reason": f"Entertainment domain ({host})",
        "category": "entertainment",
        "domain": host,
        "model": "heuristic-fallback"
    }

if __name__ == "__main__":
    test_cases = [
        ("https://www.youtube.com/watch?v=1", "Lex Fridman Podcast #400 – Jeff Bezos"),
        ("https://www.youtube.com/watch?v=2", "Huberman Lab: Tools to Optimize Your Focus | Episode 84"),
        ("https://www.youtube.com/watch?v=3", "Dwarkesh Patel: Ilya Sutskever on AGI"),
        ("https://www.youtube.com/watch?v=4", "Acquired: The Complete History of Nvidia"),
        ("https://www.youtube.com/watch?v=5", "MIT 18.06 Linear Algebra Lecture 1"),
        ("https://www.youtube.com/watch?v=6", "Craziest Dog Fails Compilation 2024"),
        ("https://www.youtube.com/shorts/xyz", "Funny Dog Meme Short"),
        ("https://tv.apple.com/show/ted-lasso", "Watch Ted Lasso Season 3 Episode 1"),
        ("https://podcasts.apple.com/us/podcast/huberman-lab/id1545953110", "Huberman Lab on Apple Podcasts"),
        ("https://open.spotify.com/episode/xyz", "The Joe Rogan Experience #2100"),
    ]

    print("--- Testing Jev Hybrid Decision Engine (with Podcast Support) ---")
    for u, t in test_cases:
        res = evaluate_tab(u, t)
        print(f"[{res['action']:8s}] ({res.get('model', 'unknown'):18s}) {t[:38]:38s} -> {res['reason']}")
