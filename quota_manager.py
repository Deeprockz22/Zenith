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

def extract_media_id(url, title):
    """
    Extracts a stable unique identifier for a TV episode or movie
    so watching the same title for 45 minutes doesn't burn multiple quota slots.
    """
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    path = parsed.path.lower()

    # Netflix: /watch/81234567
    m = re.search(r'/watch/(\d+)', path)
    if m:
        return f"netflix_{m.group(1)}"

    # Apple TV: /show/... or /episode/... or /movie/...
    m = re.search(r'/(show|episode|movie)/[^/]+/([^/?]+)', path)
    if m:
        return f"appletv_{m.group(2)[:24]}"

    # Prime Video: /detail/0S...
    m = re.search(r'/detail/([^/?]+)', path)
    if m:
        return f"prime_{m.group(1)[:20]}"

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
    Detects whether content is a TV series episode, full movie, or general clip.
    Uses regex signatures + Jev neural classification fallback.
    """
    u_low = url.lower()
    t_low = (title or "").lower()

    # 1. Check for trailers / short clips first (not eligible for full movie/series quota)
    clip_indicators = ["trailer", "teaser", "clip", "blooper", "review", "reaction", "/shorts", "/reels"]
    if any(ind in t_low or ind in u_low for ind in clip_indicators):
        return "clip"

    # 2. Strong Series / Episode indicators
    ep_patterns = [
        r'season\s*\d+', r'episode\s*\d+', r's\d+\s*e\d+', r'ep\s*\d+',
        r'/show/', r'/episode/', r'/series/', r'chapter\s*\d+'
    ]
    for pat in ep_patterns:
        if re.search(pat, t_low) or re.search(pat, u_low):
            return "episode"

    # 3. Strong Movie indicators
    movie_patterns = [
        r'full movie', r'full film', r'feature film', r'/movie/'
    ]
    for pat in movie_patterns:
        if re.search(pat, t_low) or re.search(pat, u_low):
            return "movie"

    # 4. Known streaming platforms (Netflix, Apple TV, Prime, Hulu, Disney+)
    streaming_hosts = ["netflix.com", "tv.apple.com", "hulu.com", "disneyplus.com", "primevideo.com", "max.com"]
    is_streaming = any(h in u_low for h in streaming_hosts)
    if is_streaming:
        if "movie" in t_low or "/movie/" in u_low:
            return "movie"
        return "episode"

    # 5. Jev Neural Classifier fallback if decider available
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

def check_entertainment_quota(url, title, media_type):
    """
    Checks if viewing this episode or movie is permitted under the daily quota.
    Updates the watched list automatically for newly started episodes/movies.
    """
    with _quota_lock:
        quota = load_quota()
        media_id = extract_media_id(url, title)
        now_iso = datetime.now().isoformat()

        if media_type == "episode":
            max_ep = quota.get("max_episodes", DEFAULT_MAX_EPISODES)
            watched = quota.get("episodes_watched", [])

            # Check if this exact episode was already started today
            existing = next((item for item in watched if item["id"] == media_id), None)
            if existing:
                existing["last_seen"] = now_iso
                quota["last_active_session"] = {"type": "episode", "id": media_id, "title": title}
                save_quota(quota)
                return {
                    "allowed": True,
                    "media_type": "episode",
                    "is_existing": True,
                    "used": len(watched),
                    "max": max_ep,
                    "remaining": max(0, max_ep - len(watched)),
                    "message": f"Continuing episode ({len(watched)}/{max_ep} used today)"
                }

            # New episode: check capacity
            if len(watched) < max_ep:
                watched.append({
                    "id": media_id,
                    "title": title[:70] if title else "Episode",
                    "first_seen": now_iso,
                    "last_seen": now_iso
                })
                quota["episodes_watched"] = watched
                quota["last_active_session"] = {"type": "episode", "id": media_id, "title": title}
                save_quota(quota)
                used_now = len(watched)
                rem = max(0, max_ep - used_now)
                return {
                    "allowed": True,
                    "media_type": "episode",
                    "is_existing": False,
                    "used": used_now,
                    "max": max_ep,
                    "remaining": rem,
                    "message": f"Episode {used_now}/{max_ep} started ({rem} remaining today)"
                }
            else:
                return {
                    "allowed": False,
                    "media_type": "episode",
                    "is_existing": False,
                    "used": len(watched),
                    "max": max_ep,
                    "remaining": 0,
                    "reason": f"Daily series quota reached: {len(watched)}/{max_ep} episodes watched today"
                }

        elif media_type == "movie":
            max_mov = quota.get("max_movies", DEFAULT_MAX_MOVIES)
            watched = quota.get("movies_watched", [])

            existing = next((item for item in watched if item["id"] == media_id), None)
            if existing:
                existing["last_seen"] = now_iso
                quota["last_active_session"] = {"type": "movie", "id": media_id, "title": title}
                save_quota(quota)
                return {
                    "allowed": True,
                    "media_type": "movie",
                    "is_existing": True,
                    "used": len(watched),
                    "max": max_mov,
                    "remaining": max(0, max_mov - len(watched)),
                    "message": f"Continuing movie (1/1 used today)"
                }

            if len(watched) < max_mov:
                watched.append({
                    "id": media_id,
                    "title": title[:70] if title else "Feature Movie",
                    "first_seen": now_iso,
                    "last_seen": now_iso
                })
                quota["movies_watched"] = watched
                quota["last_active_session"] = {"type": "movie", "id": media_id, "title": title}
                save_quota(quota)
                return {
                    "allowed": True,
                    "media_type": "movie",
                    "is_existing": False,
                    "used": 1,
                    "max": max_mov,
                    "remaining": 0,
                    "message": "Daily movie started (1/1 allowed today - enjoy!)"
                }
            else:
                return {
                    "allowed": False,
                    "media_type": "movie",
                    "is_existing": False,
                    "used": len(watched),
                    "max": max_mov,
                    "remaining": 0,
                    "reason": f"Daily movie quota reached: {len(watched)}/{max_mov} movie watched today"
                }

        return {"allowed": False, "reason": "General entertainment clip", "media_type": "general"}

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
        return get_quota_summary()

def set_quota_limits(max_episodes=2, max_movies=1):
    """Configures daily limits."""
    with _quota_lock:
        quota = load_quota()
        quota["max_episodes"] = max(0, int(max_episodes))
        quota["max_movies"] = max(0, int(max_movies))
        save_quota(quota)
        return get_quota_summary()
