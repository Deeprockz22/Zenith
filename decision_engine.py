#!/usr/bin/env python3
"""
FocusRedirect: Context-Aware Jev Neural Decision Engine
Powered by TypeSafe-style Jev / so1 (System One Decision Model).
Evaluates page title, URL path, and browsing trajectory with typed decisions in ~47ms.
"""

import sys
import threading
import os
import json
import subprocess
import atexit
from types import SimpleNamespace
from urllib.parse import urlparse
from history_reader import KNOWN_ENTERTAINMENT_ROOTS, KNOWN_PRODUCTIVE_ROOTS, KNOWN_PODCAST_ROOTS
from profiles import get_profile
from rag_engine import get_rag

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
_worker_process = None
_worker_lock = threading.Lock()


class JevWorkerClient:
    def __init__(self):
        self.process = None
        self.lock = threading.Lock()

    def _start(self):
        worker = os.path.join(os.path.dirname(__file__), "jev_worker.py")
        self.process = subprocess.Popen(
            [sys.executable, worker],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None,
            text=True,
            bufsize=1,
        )

    def decide(self, state, _questions):
        with self.lock:
            if self.process is None or self.process.poll() is not None:
                self._start()
            try:
                self.process.stdin.write(json.dumps({"state": state}) + "\n")
                self.process.stdin.flush()
                line = self.process.stdout.readline()
                if not line:
                    raise RuntimeError("Jev worker exited without a response")
                response = json.loads(line)
                if "error" in response:
                    raise RuntimeError(response["error"])
                return [SimpleNamespace(
                    choice=response["choice"],
                    confidence=response["confidence"],
                )]
            except (BrokenPipeError, OSError, json.JSONDecodeError) as exc:
                self.close()
                raise RuntimeError(f"Jev worker unavailable: {exc}") from exc

    def close(self):
        process, self.process = self.process, None
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()


def _close_jev_worker():
    if _worker_process is not None:
        _worker_process.close()


atexit.register(_close_jev_worker)

def get_jev_decider():
    global _decider, _is_loading, _model_ready, _worker_process
    if os.environ.get("FOCUS_ENABLE_JEV_MODEL", "").lower() not in {"1", "true", "yes"}:
        return None
    if _worker_process is not None:
        return _worker_process

    with _model_lock:
        if _worker_process is not None:
            return _worker_process
        if _is_loading:
            return None

        _is_loading = True
        try:
            print("🧠 Starting isolated Jev decision worker...")
            _worker_process = JevWorkerClient()
            _model_ready = True
            return _worker_process
        except Exception as e:
            print(f"[Jev worker error, falling back to heuristics]: {e}", file=sys.stderr)
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

    # --- TIER 1E: RAG Context Retrieval & Knowledge Engine (< 0.1ms) ---
    rag = get_rag()
    rag_context = rag.retrieve(url, title_clean, profile_id=profile.get("id"))

    # RAG Fast-Path: Verified High-Trust Creator
    if not is_risk and rag_context.get("matched_creator"):
        creator = rag_context["matched_creator"]
        if creator.get("trust", 0) >= 0.90:
            ctype = creator.get("type", "lecture")
            if ctype in allowed_types or creator.get("category") in allowed_types or profile.get("id") in ("academic", "developer"):
                return {
                    "action": "ALLOW",
                    "reason": f"RAG Verified Creator: {creator['name']} ({creator['notes'][:28]})",
                    "category": "podcast_exception" if ctype == "podcast" else "educational_exception",
                    "domain": host,
                    "model": "rag-verified-creator",
                    "rag": rag_context
                }

    # RAG Fast-Path: Direct Alignment with User's Active Study / Work Goals
    if not is_risk and rag_context.get("matched_goals"):
        top_goal = rag_context["matched_goals"][0]
        if top_goal.get("score", 0) >= 0.70:
            return {
                "action": "ALLOW",
                "reason": f"RAG User Goal: '{top_goal['topic'][:26]}' ({top_goal['score']*100:.0f}%)",
                "category": "educational_exception",
                "domain": host,
                "model": "rag-goal-aligned",
                "rag": rag_context
            }

    # RAG Fast-Path: Exact or High-Confidence Memory Recall from User Feedback
    if not is_risk and rag_context.get("few_shot_exemplars"):
        top_ex = rag_context["few_shot_exemplars"][0]
        if top_ex.get("user_override") and top_ex.get("action") == "ALLOW":
            return {
                "action": "ALLOW",
                "reason": f"RAG Memory Recall: Prior user approval for '{top_ex['title'][:26]}'",
                "category": "memory_learned_exception",
                "domain": host,
                "model": "rag-memory-recall",
                "rag": rag_context
            }

    # --- TIER 2: Jev Neural Decision Model with RAG Context Augmentation (~47ms) ---
    decider = get_jev_decider()
    if decider is not None and title_clean:
        try:
            from so1 import Choice

            # Augment Jev's System-One prompt state with retrieved RAG context & memory
            rag_summary = rag_context.get("rag_summary", "None")
            state = f'Title: "{title_clean}"\nDomain: {host}\nRetrieved RAG Context: {rag_summary}'
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
                    "reason": f"Jev+RAG ({profile['badge']}) allowed: {label} ({conf*100:.0f}%)",
                    "category": category,
                    "domain": host,
                    "model": "jev-rag-system-one",
                    "confidence": conf,
                    "rag": rag_context
                }
            else:
                # Check Daily Entertainment Quota (Max 2 episodes, 1 movie per day)
                if profile.get("id") != "zen":
                    from quota_manager import detect_media_format, check_entertainment_quota
                    media_fmt = detect_media_format(url, title_clean)
                    if media_fmt == "streaming_browse":
                        from quota_manager import has_quota_available
                        if has_quota_available():
                            return {
                                "action": "ALLOW",
                                "reason": "Streaming Catalog: Browsing (No quota consumed)",
                                "category": "entertainment_browse",
                                "domain": host,
                                "model": "quota-manager",
                                "rag": rag_context
                            }
                        else:
                            return {
                                "action": "REDIRECT",
                                "reason": "Daily entertainment quota reached: no episodes or movies remaining today",
                                "category": "entertainment",
                                "domain": host,
                                "model": "quota-manager",
                                "rag": rag_context
                            }
                    elif media_fmt in ("episode", "movie"):
                        q_res = check_entertainment_quota(url, title_clean, media_fmt)
                        if q_res.get("allowed"):
                            label = "Series Episode" if media_fmt == "episode" else "Feature Movie"
                            if not q_res.get("confirmed"):
                                reason_msg = f"Trial Playback: {label} (Running {int(q_res.get('duration_seconds', 0))}s / 60s to count)"
                            else:
                                reason_msg = f"Quota Allowed: {label} ({q_res['used']}/{q_res['max']} today)"
                            return {
                                "action": "ALLOW",
                                "reason": reason_msg,
                                "category": "entertainment_quota_allowed",
                                "domain": host,
                                "model": "quota-manager",
                                "quota_info": q_res,
                                "rag": rag_context
                            }
                        else:
                            return {
                                "action": "REDIRECT",
                                "reason": q_res.get("reason", "Daily entertainment quota reached"),
                                "category": "entertainment",
                                "domain": host,
                                "model": "quota-manager",
                                "quota_info": q_res,
                                "rag": rag_context
                            }

                return {
                    "action": "REDIRECT",
                    "reason": f"Jev+RAG ({profile['badge']}) classified as {choice} ({conf*100:.0f}%)",
                    "category": "entertainment",
                    "domain": host,
                    "model": "jev-rag-system-one",
                    "confidence": conf,
                    "rag": rag_context
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
        from quota_manager import detect_media_format, check_entertainment_quota, has_quota_available
        media_fmt = detect_media_format(url, title_clean)
        if media_fmt == "streaming_browse":
            if has_quota_available():
                return {
                    "action": "ALLOW",
                    "reason": "Streaming Catalog: Browsing (No quota consumed)",
                    "category": "entertainment_browse",
                    "domain": host,
                    "model": "quota-manager"
                }
            else:
                return {
                    "action": "REDIRECT",
                    "reason": "Daily entertainment quota reached: no episodes or movies remaining today",
                    "category": "entertainment",
                    "domain": host,
                    "model": "quota-manager"
                }
        elif media_fmt in ("episode", "movie"):
            q_res = check_entertainment_quota(url, title_clean, media_fmt)
            if q_res.get("allowed"):
                label = "Series Episode" if media_fmt == "episode" else "Feature Movie"
                if not q_res.get("confirmed"):
                    reason_msg = f"Trial Playback: {label} (Running {int(q_res.get('duration_seconds', 0))}s / 60s to count)"
                else:
                    reason_msg = f"Quota Allowed: {label} ({q_res['used']}/{q_res['max']} today)"
                return {
                    "action": "ALLOW",
                    "reason": reason_msg,
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
