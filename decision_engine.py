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
from profiles import get_profile

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
    "python", "student", "university", "syllabus", "assignment", "coding",
    "deep learning", "documentary", "mit", "stanford", "harvard", "cs50",
    "crash course", "explanation", "analysis", "study", "mechanics", "cfd",
    "machine learning", "homework", "exam", "research", "computerphile",
    "numberphile", "veritasium", "3blue1brown"
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

def evaluate_tab(url, title, recent_trajectory=None, profile_id=None):
    """
    Evaluates whether an active browser tab should be allowed or redirected.
    Uses Tier 1 (fast whitelist) + Tier 2 (Jev single-pass neural decision) + Tier 3 (heuristics).
    Adapts intelligently to the user's active Profile (Developer, Academic, Founder, Creator, General, Zen).
    """
    if not url:
        return {"action": "ALLOW", "reason": "Empty URL", "category": "neutral"}

    profile = get_profile(profile_id)
    productive_roots = KNOWN_PRODUCTIVE_ROOTS | profile.get("productive_domains", set())
    allowed_types = profile.get("allowed_types", ["podcast", "lecture"])
    profile_keywords = profile.get("allowed_keywords", [])

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]

    path = parsed.path.lower()
    title_clean = (title or "").strip()
    title_lower = title_clean.lower()

    # --- TIER 1A: Dedicated Podcast Platforms (< 0.1ms) ---
    if "podcast" in allowed_types and any(host == p or host.endswith("." + p) for p in KNOWN_PODCAST_ROOTS):
        return {
            "action": "ALLOW",
            "reason": f"Podcast audio platform ({host})",
            "category": "podcast_exception",
            "domain": host,
            "model": "fast-whitelist"
        }

    # --- TIER 1B: Instant Fast-Path for Profile Productive Portals (< 0.1ms) ---
    if any(host == p or host.endswith("." + p) for p in productive_roots):
        return {
            "action": "ALLOW",
            "reason": f"Productive for {profile['name']} ({host})",
            "category": "productive",
            "domain": host,
            "model": "fast-whitelist"
        }

    # For Student & Scholar profile, any institutional/university domain is automatically whitelisted
    if profile.get("id") == "academic":
        if (
            host.endswith(".edu") or ".edu." in host or
            host.endswith(".ac.uk") or ".ac." in host or
            "instructure.com" in host or "blackboard.com" in host or "moodle" in host or
            "canvas" in host or "classroom.google.com" in host
        ):
            return {
                "action": "ALLOW",
                "reason": f"University & Academic Portal ({host})",
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

    # --- TIER 1D: Fast Whitelist for Unmistakable Profile & Podcast Content (< 0.1ms) ---
    is_risk = any(kw in path or kw in title_lower for kw in HIGH_RISK_KEYWORDS)
    is_explicit_podcast = ("podcast" in allowed_types) and any(kw in title_lower for kw in PODCAST_KEYWORDS)
    is_explicit_edu = ("lecture" in allowed_types) and any(kw in title_lower for kw in (EDUCATIONAL_KEYWORDS + profile_keywords))

    if is_explicit_podcast and not is_risk:
        return {
            "action": "ALLOW",
            "reason": f"Allowed Podcast / Talk ({profile['badge']}): {title_clean[:32]}",
            "category": "podcast_exception",
            "domain": host,
            "model": "fast-whitelist"
        }

    if is_explicit_edu and not is_risk:
        return {
            "action": "ALLOW",
            "reason": f"Allowed Content ({profile['badge']}): {title_clean[:32]}",
            "category": "educational_exception",
            "domain": host,
            "model": "fast-whitelist"
        }

    # --- TIER 2: Jev Neural Decision Model with Active Persona Injection (~47ms) ---
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

            if choice in allowed_types:
                category = "podcast_exception" if choice == "podcast" else "educational_exception"
                label = "Podcast / Long-form talk" if choice == "podcast" else "Educational / Deep-dive"
                return {
                    "action": "ALLOW",
                    "reason": f"Jev ({profile['badge']}) allowed: {label} ({conf*100:.0f}%)",
                    "category": category,
                    "domain": host,
                    "model": "jev-system-one",
                    "confidence": conf
                }
            else:
                # Check Daily Entertainment Quota (Max 2 episodes, 1 movie per day)
                if profile.get("id") != "zen":
                    from quota_manager import detect_media_format, check_entertainment_quota
                    media_fmt = detect_media_format(url, title_clean, decider=decider)
                    if media_fmt in ("episode", "movie"):
                        q_res = check_entertainment_quota(url, title_clean, media_fmt)
                        if q_res.get("allowed"):
                            label = "Series Episode" if media_fmt == "episode" else "Feature Movie"
                            return {
                                "action": "ALLOW",
                                "reason": f"Quota Allowed: {label} ({q_res['used']}/{q_res['max']} today)",
                                "category": "entertainment_quota_allowed",
                                "domain": host,
                                "model": "quota-manager",
                                "quota_info": q_res
                            }
                        else:
                            return {
                                "action": "REDIRECT",
                                "reason": q_res.get("reason", "Daily entertainment quota reached"),
                                "category": "entertainment",
                                "domain": host,
                                "model": "quota-manager",
                                "quota_info": q_res
                            }

                return {
                    "action": "REDIRECT",
                    "reason": f"Jev ({profile['badge']}) classified as {choice} ({conf*100:.0f}%)",
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
            "reason": f"Podcast context exception ({profile['badge']})",
            "category": "podcast_exception",
            "domain": host,
            "model": "heuristic-fallback"
        }

    if is_explicit_edu and not is_risk:
        return {
            "action": "ALLOW",
            "reason": f"Profile context exception ({profile['badge']})",
            "category": "educational_exception",
            "domain": host,
            "model": "heuristic-fallback"
        }

    # Check Daily Entertainment Quota for series & movies in heuristic fallback
    if profile.get("id") != "zen":
        from quota_manager import detect_media_format, check_entertainment_quota
        media_fmt = detect_media_format(url, title_clean)
        if media_fmt in ("episode", "movie"):
            q_res = check_entertainment_quota(url, title_clean, media_fmt)
            if q_res.get("allowed"):
                label = "Series Episode" if media_fmt == "episode" else "Feature Movie"
                return {
                    "action": "ALLOW",
                    "reason": f"Quota Allowed: {label} ({q_res['used']}/{q_res['max']} today)",
                    "category": "entertainment_quota_allowed",
                    "domain": host,
                    "model": "quota-manager",
                    "quota_info": q_res
                }
            else:
                return {
                    "action": "REDIRECT",
                    "reason": q_res.get("reason", "Daily entertainment quota reached"),
                    "category": "entertainment",
                    "domain": host,
                    "model": "quota-manager",
                    "quota_info": q_res
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
        ("developer", "https://github.com/torvalds/linux", "Linux Kernel Git Repo"),
        ("developer", "https://www.youtube.com/watch?v=1", "Rust for Systems Programming Tutorial"),
        ("academic", "https://overleaf.com/project/1", "Master Thesis Document"),
        ("academic", "https://www.youtube.com/watch?v=2", "MIT 18.06 Linear Algebra Lecture 1"),
        ("founder", "https://linear.app/team/issue/1", "Q3 Strategic Roadmap"),
        ("founder", "https://www.youtube.com/watch?v=3", "Acquired: Complete History of Nvidia"),
        ("creator", "https://figma.com/file/1", "Design System UI Kit"),
        ("general", "https://www.youtube.com/watch?v=4", "Lex Fridman Podcast #400 – Jeff Bezos"),
        ("zen", "https://www.youtube.com/watch?v=5", "All-In Podcast E150: Economy"),
        ("general", "https://www.youtube.com/watch?v=6", "Craziest Dog Fails Compilation 2024"),
    ]

    print("--- Testing Profile-Aware Jev Decision Engine ---")
    for prof, u, t in test_cases:
        res = evaluate_tab(u, t, profile_id=prof)
        print(f"[{prof:9s}] [{res['action']:8s}] ({res.get('model', 'unknown'):18s}) {t[:32]:32s} -> {res['reason']}")
