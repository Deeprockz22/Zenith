#!/usr/bin/env python3
"""
FocusRedirect: History Intelligence Engine
Reads local browser SQLite history (Arc, Chrome, Brave, Edge),
aggregates real habits, and detects doomscroll patterns.
"""

import os
import shutil
import sqlite3
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from urllib.parse import urlparse

HISTORY_PATHS = [
    ("Arc", os.path.expanduser("~/Library/Application Support/Arc/User Data/Default/History")),
    ("Google Chrome", os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/History")),
    ("Brave Browser", os.path.expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser/Default/History")),
    ("Microsoft Edge", os.path.expanduser("~/Library/Application Support/Microsoft Edge/Default/History")),
]

KNOWN_ENTERTAINMENT_ROOTS = {
    "netflix.com", "tv.apple.com", "youtube.com", "youtu.be",
    "instagram.com", "threads.net", "threads.com", "x.com", "twitter.com",
    "reddit.com", "tiktok.com", "twitch.tv", "facebook.com", "hulu.com",
    "disneyplus.com", "primevideo.com", "pinterest.com"
}

KNOWN_PODCAST_ROOTS = {
    "podcasts.apple.com", "open.spotify.com", "spotify.com",
    "overcast.fm", "pocketcasts.com", "podbean.com", "castbox.fm",
    "stitcher.com", "audible.com", "ted.com", "npr.org", "bbc.co.uk"
}

KNOWN_PRODUCTIVE_ROOTS = {
    "github.com", "overleaf.com", "canvas.instructure.com", "instructure.com",
    "canvaslms.com", "sso.canvaslms.com", "classroom.google.com", "blackboard.com",
    "moodle.org", "quizlet.com", "coursera.org", "edx.org", "khanacademy.org",
    "notion.so", "chatgpt.com", "claude.ai", "arxiv.org", "scholar.google.com",
    "stackoverflow.com", "mail.google.com", "docs.google.com", "leetcode.com",
    "huggingface.co", "linear.app", "podcasts.apple.com", "open.spotify.com",
    "spotify.com", "overcast.fm", "pocketcasts.com", "podbean.com", "castbox.fm",
    "stitcher.com", "audible.com", "ted.com", "npr.org"
}

from profiles import get_profile

def get_active_history_db():
    for name, path in HISTORY_PATHS:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return name, path
    return None, None

def analyze_history(limit=500, profile_id=None):
    """Parses browser history to extract habits, time sinks, and danger hours based on active profile."""
    profile = get_profile(profile_id)
    profile_productive = KNOWN_PRODUCTIVE_ROOTS | profile.get("productive_domains", set())

    browser_name, db_path = get_active_history_db()
    if not db_path:
        return {
            "browser": "None detected",
            "profile": profile.get("id"),
            "top_distractions": [],
            "top_productive": [],
            "hourly_distraction_distribution": {},
            "peak_hour": None,
            "recent_trajectory": []
        }

    tmp_db = None
    try:
        fd, tmp_db = tempfile.mkstemp(prefix="focus_hist_", suffix=".sqlite")
        os.close(fd)
        shutil.copy2(db_path, tmp_db)
        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()

        # Fetch recent visits with timestamps
        # Chrome stores timestamp as microseconds since Jan 1, 1601 UTC
        cursor.execute("""
            SELECT url, title, visit_count, last_visit_time
            FROM urls
            WHERE last_visit_time > 0
            ORDER BY last_visit_time DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

        distraction_counts = Counter()
        productive_counts = Counter()
        hourly_distractions = defaultdict(int)
        recent_trajectory = []

        for url, title, visit_count, raw_time in rows:
            # Convert WebKit / Chrome epoch to python datetime
            unix_sec = (raw_time / 1000000.0) - 11644473600
            visit_dt = datetime.fromtimestamp(max(0, unix_sec))

            parsed = urlparse(url)
            host = (parsed.hostname or "").lower()
            if host.startswith("www."):
                host = host[4:]

            if not host:
                continue

            # Classify host
            is_edu_domain = (
                host.endswith(".edu") or ".edu." in host or
                host.endswith(".ac.uk") or ".ac." in host or
                "instructure.com" in host or "blackboard.com" in host or "moodle" in host or
                "canvas" in host
            )
            is_distraction = any(host == d or host.endswith("." + d) for d in KNOWN_ENTERTAINMENT_ROOTS)
            is_productive = is_edu_domain or any(host == p or host.endswith("." + p) for p in profile_productive)

            if is_distraction:
                distraction_counts[host] += visit_count
                hourly_distractions[visit_dt.hour] += 1
            elif is_productive:
                productive_counts[host] += visit_count

            if len(recent_trajectory) < 20:
                recent_trajectory.append({
                    "url": url,
                    "title": title or host,
                    "host": host,
                    "is_distraction": is_distraction,
                    "timestamp": visit_dt.isoformat(),
                    "time": visit_dt.strftime("%H:%M")
                })

        conn.close()

        # Find peak distraction window
        peak_hour = None
        if hourly_distractions:
            sorted_hours = sorted(hourly_distractions.items(), key=lambda x: x[1], reverse=True)
            peak_h = sorted_hours[0][0]
            peak_hour = f"{peak_h:02d}:00 – {(peak_h+1)%24:02d}:00"

        return {
            "browser": browser_name,
            "top_distractions": [{"domain": d, "count": c} for d, c in distraction_counts.most_common(6)],
            "top_productive": [{"domain": d, "count": c} for d, c in productive_counts.most_common(6)],
            "hourly_distraction_distribution": dict(hourly_distractions),
            "peak_hour": peak_hour or "None detected",
            "recent_trajectory": recent_trajectory
        }
    except Exception as e:
        return {"error": str(e), "browser": browser_name or "Unknown"}
    finally:
        if tmp_db and os.path.exists(tmp_db):
            try:
                os.remove(tmp_db)
            except Exception:
                pass

def check_recent_doomscroll_loop(threshold_count=3, window_minutes=15):
    """Returns True if the user has visited threshold_count distraction domains within window_minutes."""
    analysis = analyze_history(limit=50)
    cutoff = datetime.now() - timedelta(minutes=window_minutes)

    distraction_events = []
    for item in analysis.get("recent_trajectory", []):
        if not item.get("is_distraction"):
            continue
        try:
            visit_dt = datetime.fromisoformat(item["timestamp"])
        except (KeyError, TypeError, ValueError):
            # Ignore entries from older cached data that has no timestamp.
            continue
        if visit_dt >= cutoff:
            distraction_events.append(item)

    return len(distraction_events) >= threshold_count, len(distraction_events)

if __name__ == "__main__":
    import json
    data = analyze_history()
    print(json.dumps(data, indent=2))
