#!/usr/bin/env python3
"""
FocusRedirect: Entertainment Quota & Mindful Allowance Engine
Tracks daily TV series episodes (max 2/day) and movies (max 1/day)
with intelligent session tracking to prevent binge loops.
"""

import hashlib
import json
import os
import re
import sys
import threading
from datetime import datetime
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTA_FILE = os.path.join(BASE_DIR, "entertainment_quota.json")

DEFAULT_MAX_EPISODES = 2
DEFAULT_MAX_MOVIES = 1

_quota_lock = threading.RLock()

def get_today_str():
    return datetime.now().strftime("%Y-%m-%d")

def load_quota():
    """Loads daily quota data, resetting automatically if a new day has arrived."""
    today = get_today_str()
    default_quota = {
        "date": today,
        "max_episodes": DEFAULT_MAX_EPISODES,
        "max_movies": DEFAULT_MAX_MOVIES,
        "episodes_watched": [],
        "movies_watched": [],
        "last_active_session": None
    }

    if os.path.exists(QUOTA_FILE):
        try:
            with open(QUOTA_FILE, "r") as f:
                data = json.load(f)
                if data.get("date") == today:
                    # Same day, retain state
                    return data
                else:
                    # New day: retain custom max limits but reset watched lists
                    default_quota["max_episodes"] = data.get("max_episodes", DEFAULT_MAX_EPISODES)
                    default_quota["max_movies"] = data.get("max_movies", DEFAULT_MAX_MOVIES)
                    save_quota(default_quota)
                    return default_quota
        except Exception as e:
            print(f"[Quota load error]: {e}", file=sys.stderr)

    save_quota(default_quota)
    return default_quota

def save_quota(data):
    try:
        with open(QUOTA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[Quota save error]: {e}", file=sys.stderr)
import time

_active_playback_tracker = {}
_tracker_lock = threading.Lock()
RUNNING_CONFIRMATION_SECONDS = 60.0

def is_streaming_catalog_browse(url, title):
    """
    Detects if the user is merely browsing a streaming catalog,
    homepage, search results, or show info page rather than playing video.
    """
    u_low = (url or "").lower()
    t_clean = (title or "").strip()
    t_low = t_clean.lower()
    parsed = urlparse(url)
    path = (parsed.path or "").lower()
    host = (parsed.hostname or "").lower()

    # Generic brand titles (homepage browsing)
    generic_brand_titles = [
        "netflix", "apple tv", "apple tv+", "prime video", "amazon prime video",
        "hulu", "disney+", "disney plus", "max", "hbo max", "youtube"
    ]
    if t_low in generic_brand_titles or t_clean in ("\u200eApple TV", "\u200eApple TV+"):
        return True

    # Platform-specific browsing signatures
    if "netflix.com" in host:
        # Netflix active player is strictly on /watch/
        if "/watch/" not in path:
            return True

    elif "tv.apple.com" in host:
        # Apple TV active player is on /episode/ or /movie/ (and has title detailing the media)
        # Browsing paths: /, /us/room/, /channel/, /show/, /search
        if not ("/episode/" in path or "/movie/" in path):
            return True
        if path.rstrip("/") in ("/show", "/episode", "/movie"):
            return True

    elif "primevideo.com" in host or ("amazon." in host and "/video/" in path):
        # Prime active player is on /playback/ or /watch/
        if "/playback/" not in path and "/watch/" not in path:
            return True

    elif "disneyplus.com" in host or "hulu.com" in host or "max.com" in host:
        # Player is on /play/ or /video/ or /watch/
        if not any(p in path for p in ["/play/", "/video/", "/watch/"]):
            return True

    elif "youtube.com" in host:
        if "/watch" not in path:
            return True

    return False

def extract_media_id(url, title):
    """
    Extracts a stable unique identifier for a TV episode or movie
    so watching the same title for 45 minutes doesn't burn multiple quota slots.
    """
    parsed = urlparse(url)
    path = (parsed.path or "").lower()

    # Netflix: /watch/81234567
    m = re.search(r'/watch/(\d+)', path)
    if m:
        return f"netflix_{m.group(1)}"

    # Apple TV active player: /episode/... or /movie/...
    m = re.search(r'/(episode|movie)/[^/]+/([^/?]+)', path)
    if m:
        return f"appletv_{m.group(1)}_{m.group(2)[:24]}"

    # Prime Video: /playback/ or /watch/
    m = re.search(r'/(playback|watch)/([^/?]+)', path)
    if m:
        return f"prime_{m.group(2)[:20]}"

    # YouTube: ?v=xyz
    m = re.search(r'[?&]v=([^&]+)', parsed.query)
    if m:
        return f"yt_{m.group(1)}"

    # Fallback to normalized title hash
    clean_title = re.sub(r'[^a-zA-Z0-9]', '', (title or "").lower())
    if clean_title:
        h = hashlib.md5(clean_title[:40].encode('utf-8')).hexdigest()[:12]
        return f"title_{h}"

    return f"url_{hashlib.md5(url.encode('utf-8')).hexdigest()[:12]}"

def detect_media_format(url, title, decider=None):
    """
    Detects whether content is a TV series episode, full movie,
    streaming catalog browsing, or general clip.
    """
    u_low = (url or "").lower()
    t_low = (title or "").lower()

    # 1. First check if it's just browsing the catalog
    if is_streaming_catalog_browse(url, title):
        return "streaming_browse"

    # 2. Check for trailers / short clips first (not eligible for full movie/series quota)
    clip_indicators = ["trailer", "teaser", "clip", "blooper", "review", "reaction", "/shorts", "/reels"]
    if any(ind in t_low or ind in u_low for ind in clip_indicators):
        return "clip"

    # 3. Strong Series / Episode indicators
    ep_patterns = [
        r'season\s*\d+', r'episode\s*\d+', r's\d+\s*e\d+', r'ep\s*\d+',
        r'/episode/', r'chapter\s*\d+'
    ]
    for pat in ep_patterns:
        if re.search(pat, t_low) or re.search(pat, u_low):
            return "episode"

    # 4. Strong Movie indicators
    movie_patterns = [
        r'full movie', r'full film', r'feature film', r'/movie/'
    ]
    for pat in movie_patterns:
        if re.search(pat, t_low) or re.search(pat, u_low):
            return "movie"

    # 5. Known streaming platforms on active playback URLs
    streaming_hosts = ["netflix.com", "tv.apple.com", "hulu.com", "disneyplus.com", "primevideo.com", "max.com"]
    is_streaming = any(h in u_low for h in streaming_hosts)
    if is_streaming:
        # On active playback page (/watch/, /play/, etc.)
        if "movie" in t_low or "/movie/" in u_low:
            return "movie"
        return "episode"

    # 6. Jev Neural Classifier fallback if decider available
    if decider is not None and title:
        try:
            from so1 import Choice
            q = [Choice("Format", ["tv_episode", "full_movie", "clip_or_trailer", "podcast"])]
            ans = decider.decide(f'Title: "{title}"', q)[0]
            if ans.choice == "tv_episode":
                return "episode"
            elif ans.choice == "full_movie":
                return "movie"
            elif ans.choice == "clip_or_trailer":
                return "clip"
        except Exception:
            pass

    return "general"

def has_quota_available():
    """Returns True if there is remaining capacity for at least one episode or movie."""
    with _quota_lock:
        quota = load_quota()
        max_ep = quota.get("max_episodes", DEFAULT_MAX_EPISODES)
        max_mov = quota.get("max_movies", DEFAULT_MAX_MOVIES)
        episodes = quota.get("episodes_watched", [])
        movies = quota.get("movies_watched", [])
        return (len(episodes) < max_ep) or (len(movies) < max_mov)

def update_playback_session(media_id, media_type, title):
    """
    Tracks elapsed active playback time for a media ID.
    Returns (confirmed_status, duration_seconds, just_confirmed_bool)
    """
    now = time.time()
    with _tracker_lock:
        if media_id not in _active_playback_tracker:
            _active_playback_tracker[media_id] = {
                "first_seen": now,
                "last_seen": now,
                "duration": 0.0,
                "media_type": media_type,
                "title": title,
                "confirmed": False
            }
            return False, 0.0, False

        tracker = _active_playback_tracker[media_id]
        delta = now - tracker["last_seen"]
        # Only accumulate if poller saw it within the last 4.0 seconds (i.e. currently active tab)
        if 0 < delta <= 4.0:
            tracker["duration"] += delta
        elif delta > 300.0:
            # If user was gone for more than 5 minutes and came back, reset trial counter if not confirmed
            if not tracker["confirmed"]:
                tracker["duration"] = 0.0
                tracker["first_seen"] = now

        tracker["last_seen"] = now

        if not tracker["confirmed"] and tracker["duration"] >= RUNNING_CONFIRMATION_SECONDS:
            tracker["confirmed"] = True
            return True, tracker["duration"], True  # Just confirmed!

        return tracker["confirmed"], tracker["duration"], False

def check_entertainment_quota(url, title, media_type):
    """
    Checks if viewing this episode or movie is permitted under the daily quota.
    CRITICAL: Does NOT count an episode or movie as consumed until it has actively
    been running for at least 60 seconds of playback time.
    """
    with _quota_lock:
        quota = load_quota()
        media_id = extract_media_id(url, title)
        now_iso = datetime.now().isoformat()
        label = "Series Episode" if media_type == "episode" else "Feature Movie"
        list_key = "episodes_watched" if media_type == "episode" else "movies_watched"
        max_key = "max_episodes" if media_type == "episode" else "max_movies"
        default_max = DEFAULT_MAX_EPISODES if media_type == "episode" else DEFAULT_MAX_MOVIES

        max_val = quota.get(max_key, default_max)
        watched = quota.get(list_key, [])

        # 1. Check if already confirmed today
        existing = next((item for item in watched if item["id"] == media_id), None)
        if existing:
            existing["last_seen"] = now_iso
            quota["last_active_session"] = {"type": media_type, "id": media_id, "title": title}
            save_quota(quota)
            return {
                "allowed": True,
                "media_type": media_type,
                "is_existing": True,
                "confirmed": True,
                "just_confirmed": False,
                "used": len(watched),
                "max": max_val,
                "remaining": max(0, max_val - len(watched)),
                "message": f"Continuing {label} ({len(watched)}/{max_val} used today)"
            }

        # 2. If not already confirmed, check if daily capacity is exhausted
        if len(watched) >= max_val:
            return {
                "allowed": False,
                "media_type": media_type,
                "is_existing": False,
                "confirmed": False,
                "just_confirmed": False,
                "used": len(watched),
                "max": max_val,
                "remaining": 0,
                "reason": f"Daily {label} quota reached: {len(watched)}/{max_val} watched today"
            }

        # 3. User has capacity: track running playback duration
        is_confirmed, duration, just_confirmed = update_playback_session(media_id, media_type, title)

        if just_confirmed:
            # Reached 60s of active running playback -> NOW officially record into watched quota
            watched.append({
                "id": media_id,
                "title": title[:70] if title else label,
                "first_seen": datetime.fromtimestamp(time.time() - duration).isoformat(),
                "confirmed_at": now_iso,
                "last_seen": now_iso
            })
            quota[list_key] = watched
            quota["last_active_session"] = {"type": media_type, "id": media_id, "title": title}
            save_quota(quota)
            used_now = len(watched)
            rem = max(0, max_val - used_now)
            return {
                "allowed": True,
                "media_type": media_type,
                "is_existing": False,
                "confirmed": True,
                "just_confirmed": True,
                "used": used_now,
                "max": max_val,
                "remaining": rem,
                "message": f"{label} {used_now}/{max_val} started ({rem} remaining today)"
            }
        elif is_confirmed:
            # Already confirmed in memory
            return {
                "allowed": True,
                "media_type": media_type,
                "is_existing": True,
                "confirmed": True,
                "just_confirmed": False,
                "used": len(watched),
                "max": max_val,
                "remaining": max(0, max_val - len(watched)),
                "message": f"Running {label} ({len(watched)}/{max_val} used today)"
            }
        else:
            # In the 0-60s running trial: ALLOW playback, but DO NOT count against quota yet!
            return {
                "allowed": True,
                "media_type": media_type,
                "is_existing": False,
                "confirmed": False,
                "just_confirmed": False,
                "duration_seconds": round(duration, 1),
                "used": len(watched),
                "max": max_val,
                "remaining": max(0, max_val - len(watched)),
                "message": f"Starting {label}... Running {int(duration)}s / 60s to count"
            }

def get_quota_summary():
    """Returns a status summary for API and dashboard rendering."""
    with _quota_lock:
        quota = load_quota()
        episodes = quota.get("episodes_watched", [])
        movies = quota.get("movies_watched", [])
        max_ep = quota.get("max_episodes", DEFAULT_MAX_EPISODES)
        max_mov = quota.get("max_movies", DEFAULT_MAX_MOVIES)

        return {
            "date": quota.get("date"),
            "episodes_used": len(episodes),
            "episodes_max": max_ep,
            "episodes_remaining": max(0, max_ep - len(episodes)),
            "movies_used": len(movies),
            "movies_max": max_mov,
            "movies_remaining": max(0, max_mov - len(movies)),
            "episodes_list": episodes,
            "movies_list": movies
        }

def reset_quota_today():
    """Manually resets today's entertainment quota."""
    with _quota_lock:
        quota = load_quota()
        quota["episodes_watched"] = []
        quota["movies_watched"] = []
        quota["last_active_session"] = None
        save_quota(quota)
    with _tracker_lock:
        _active_playback_tracker.clear()
    return get_quota_summary()

def set_quota_limits(max_episodes=2, max_movies=1):
    """Configures daily limits."""
    with _quota_lock:
        quota = load_quota()
        quota["max_episodes"] = max(0, int(max_episodes))
        quota["max_movies"] = max(0, int(max_movies))
        save_quota(quota)
        return get_quota_summary()
