#!/usr/bin/env python3
"""
FocusRedirect: Context-Aware Jev Neural Decision Engine
Powered by TypeSafe-style Jev / so1 (System One Decision Model).
Evaluates page title, URL path, and browsing trajectory with typed decisions in ~47ms.
"""

import sys
import threading
from urllib.parse import urlparse
from history_reader import KNOWN_ENTERTAINMENT_ROOTS, KNOWN_PRODUCTIVE_ROOTS

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
    Uses Tier 1 (fast whitelist) + Tier 2 (Jev single-pass neural decision).
    """
    if not url:
        return {"action": "ALLOW", "reason": "Empty URL", "category": "neutral"}

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]

    path = parsed.path.lower()
    title_clean = (title or "").strip()

    # --- TIER 1: Instant Fast-Path for Known Productive Portals (< 0.1ms) ---
    if any(host == p or host.endswith("." + p) for p in KNOWN_PRODUCTIVE_ROOTS):
        return {
            "action": "ALLOW",
            "reason": f"Productive portal ({host})",
            "category": "productive",
            "model": "fast-whitelist"
        }

    # Only invoke deep analysis for entertainment or distraction domains
    is_entertainment = any(host == e or host.endswith("." + e) for e in KNOWN_ENTERTAINMENT_ROOTS)
    if not is_entertainment:
        return {
            "action": "ALLOW",
            "reason": "Neutral domain",
            "category": "neutral",
            "model": "fast-whitelist"
        }

    # --- TIER 2: Jev Neural Decision Model (~47ms single forward pass) ---
    decider = get_jev_decider()
    if decider is not None and title_clean:
        try:
            from so1 import Choice, yes_no

            # Format state representation for Jev
            recent_context = ""
            if recent_trajectory:
                recent_hosts = [item.get("title", "")[:25] for item in recent_trajectory[:4]]
                recent_context = " | Prior pages: " + ", ".join(recent_hosts)

            state = f"Page Title: {title_clean} | Domain: {host} | Path: {path}{recent_context}"
            questions = [
                Choice("Intent", ["study_or_work", "casual_entertainment", "doomscrolling"]),
                yes_no("Should redirect to focus?")
            ]

            answers = decider.decide(state, questions)
            intent_ans = answers[0]
            redirect_ans = answers[1]

            intent = intent_ans.choice
            intent_conf = intent_ans.confidence
            should_redirect = redirect_ans.choice == "yes"

            if intent == "study_or_work" and intent_conf >= 0.55:
                return {
                    "action": "ALLOW",
                    "reason": f"Jev allowed: Educational intent ({intent_conf*100:.0f}% confidence)",
                    "category": "educational_exception",
                    "domain": host,
                    "model": "jev-system-one",
                    "confidence": intent_conf
                }
            else:
                return {
                    "action": "REDIRECT",
                    "reason": f"Jev classified as {intent} ({intent_conf*100:.0f}% confidence)",
                    "category": "entertainment",
                    "domain": host,
                    "model": "jev-system-one",
                    "confidence": intent_conf
                }
        except Exception as e:
            # Fallback to heuristics if neural pass fails
            pass

    # --- TIER 3: Semantic Heuristic Fallback (< 1ms) ---
    educational_keywords = [
        "tutorial", "course", "lecture", "how to", "engineering", "math",
        "python", "chalmers", "coding", "deep learning", "documentary", "mit",
        "stanford", "cs50", "crash course", "explanation", "analysis", "study",
        "mechanics", "cfd", "machine learning", "homework", "exam", "research"
    ]
    high_risk_keywords = [
        "/shorts", "/reels", "funny", "meme", "prank", "reaction", "gaming",
        "trailer", "season", "episode", "stream", "celebrity", "gossip", "trending"
    ]

    title_lower = title_clean.lower()
    is_edu = any(kw in title_lower for kw in educational_keywords)
    is_risk = any(kw in path or kw in title_lower for kw in high_risk_keywords)

    if is_edu and not is_risk:
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
        ("https://www.youtube.com/watch?v=1", "MIT 18.06 Linear Algebra Lecture 1"),
        ("https://www.youtube.com/watch?v=2", "Craziest Dog Fails Compilation"),
        ("https://tv.apple.com/show/ted-lasso", "Watch Ted Lasso Season 3 Episode 1"),
        ("https://github.com/HeyPuter/puter", "HeyPuter/puter repo"),
    ]

    print("--- Testing Jev Hybrid Decision Engine ---")
    for u, t in test_cases:
        res = evaluate_tab(u, t)
        print(f"[{res['action']:8s}] ({res.get('model', 'unknown'):18s}) {t[:35]:35s} -> {res['reason']}")
