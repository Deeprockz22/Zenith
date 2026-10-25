#!/usr/bin/env python3
"""
FocusRedirect: Context-Aware Browser History & Tab Decision Daemon
Monitors active browser tabs, evaluates page titles & URLs, reads local
history to detect doomscroll loops, and serves the Focus Zone Dashboard.
"""

import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

from decision_engine import evaluate_tab
from history_reader import analyze_history
from profiles import get_profile, serialize_profile, list_profiles, PROFILES, DEFAULT_PROFILE_ID
from quota_manager import get_quota_summary, reset_quota_today, set_quota_limits
from rag_engine import get_rag

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATS_FILE = os.path.join(BASE_DIR, "focus_stats.json")
DASHBOARD_FILE = os.path.join(BASE_DIR, "dashboard.html")
REDIRECT_URL = "http://localhost:5050"
PORT = 5050

SUPPORTED_BROWSERS = [
    "Google Chrome",
    "Arc",
    "Safari",
    "Brave Browser",
    "Microsoft Edge"
]

stats_lock = threading.Lock()

def load_stats():
    default_stats = {
        "total_intercepted": 0,
        "site_counts": {},
        "history": [],
        "exceptions_allowed": [],
        "active_profile": DEFAULT_PROFILE_ID
    }
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                d = json.load(f)
                if "active_profile" not in d:
                    d["active_profile"] = DEFAULT_PROFILE_ID
                return d
        except Exception:
            pass
    return default_stats

def save_stats(data):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[Error saving stats] {e}", file=sys.stderr)

stats = load_stats()


def applescript_string(value, limit=120):
    """Return a safely quoted AppleScript string literal."""
    text = str(value or "")[:limit]
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


# Cached history analysis (refreshed periodically)
cached_history_data = {}
history_lock = threading.Lock()

def refresh_history_cache():
    global cached_history_data
    try:
        with stats_lock:
            prof_id = stats.get("active_profile", DEFAULT_PROFILE_ID)
        data = analyze_history(limit=400, profile_id=prof_id)
        with history_lock:
            cached_history_data = data
    except Exception as e:
        print(f"[History cache error] {e}", file=sys.stderr)

def notify_user(domain, reason=""):
    subtitle = reason if reason else "Entertainment Intercepted"
    apple_script = (
        f"display notification {applescript_string(f'Redirected from {domain} to your Focus Zone.', 180)} "
        f"with title {applescript_string('Focus Mode Active 🎯')} "
        f"subtitle {applescript_string(subtitle, 35)}"
    )
    subprocess.run(["osascript", "-e", apple_script], capture_output=True)

def record_intercept(domain, reason, title):
    with stats_lock:
        stats["total_intercepted"] += 1
        stats["site_counts"][domain] = stats["site_counts"].get(domain, 0) + 1
        stats["history"].append({
            "domain": domain,
            "title": title[:60] if title else domain,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        if len(stats["history"]) > 100:
            stats["history"] = stats["history"][-100:]
        save_stats(stats)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚫 Intercepted: {domain} | {reason}")
    notify_user(domain, reason)

def record_allowed_exception(domain, title, reason):
    with stats_lock:
        if "exceptions_allowed" not in stats:
            stats["exceptions_allowed"] = []
        stats["exceptions_allowed"].append({
            "domain": domain,
            "title": title[:60] if title else domain,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        if len(stats["exceptions_allowed"]) > 50:
            stats["exceptions_allowed"] = stats["exceptions_allowed"][-50:]
        save_stats(stats)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Allowed Context Exception: {title[:40]} ({domain})")

def get_active_browser_tab():
    """Detects frontmost app and gets current tab (title, url)."""
    script = '''
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
    end tell
    return frontApp
    '''
    res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if res.returncode != 0:
        return None, "", ""
    front_app = res.stdout.strip()
    if front_app not in SUPPORTED_BROWSERS:
        return None, "", ""

    if front_app == "Safari":
        tab_script = '''
        tell application "Safari"
            if (count of windows) > 0 then
                return (name of current tab of front window) & " ||| " & (URL of current tab of front window)
            end if
        end tell
        return ""
        '''
    else:
        # Chromium browsers
        tab_script = f'''
        tell application "{front_app}"
            if (count of windows) > 0 then
                return (title of active tab of front window) & " ||| " & (URL of active tab of front window)
            end if
        end tell
        return ""
        '''

    tab_res = subprocess.run(["osascript", "-e", tab_script], capture_output=True, text=True)
    if tab_res.returncode == 0 and " ||| " in tab_res.stdout:
        parts = tab_res.stdout.strip().split(" ||| ", 1)
        return front_app, parts[0].strip(), parts[1].strip()
    return None, "", ""

def redirect_active_tab(browser_name, target_url):
    if browser_name == "Safari":
        redirect_script = f'''
        tell application "Safari"
            if (count of windows) > 0 then
                set URL of current tab of front window to "{target_url}"
            end if
        end tell
        '''
    else:
        redirect_script = f'''
        tell application "{browser_name}"
            if (count of windows) > 0 then
                set URL of active tab of front window to "{target_url}"
            end if
        end tell
        '''
    subprocess.run(["osascript", "-e", redirect_script], capture_output=True)

def tab_watcher_loop():
    print("👁️  Context-Aware watcher started (monitoring Arc, Chrome, Safari, Brave, Edge)...")
    last_intercepted_url = ""
    last_intercept_time = 0
    last_history_sync = 0

    while True:
        try:
            now = time.time()
            # Periodically refresh history cache every 60 seconds
            if now - last_history_sync > 60:
                last_history_sync = now
                threading.Thread(target=refresh_history_cache, daemon=True).start()

            browser, title, url = get_active_browser_tab()
            if browser and url:
                with history_lock:
                    trajectory = cached_history_data.get("recent_trajectory", [])

                with stats_lock:
                    active_prof = stats.get("active_profile", DEFAULT_PROFILE_ID)

                decision = evaluate_tab(url, title, recent_trajectory=trajectory, profile_id=active_prof)
                action = decision.get("action")
                domain = decision.get("domain", "")

                if action == "REDIRECT":
                    if url != last_intercepted_url or (now - last_intercept_time) > 2.0:
                        last_intercepted_url = url
                        last_intercept_time = now
                        redirect_active_tab(browser, REDIRECT_URL)
                        record_intercept(domain, decision.get("reason", "Entertainment"), title)
                elif decision.get("category") in ("educational_exception", "podcast_exception", "memory_learned_exception"):
                    # Record exception once per session
                    if url != last_intercepted_url:
                        last_intercepted_url = url
                        label = "Podcast" if decision.get("category") == "podcast_exception" else ("Memory Override" if decision.get("category") == "memory_learned_exception" else "Educational")
                        record_allowed_exception(domain, title, decision.get("reason", label))
                elif decision.get("category") == "entertainment_quota_allowed":
                    # Record entertainment quota exception
                    if url != last_intercepted_url:
                        last_intercepted_url = url
                        reason = decision.get("reason", "Daily Quota Allowed")
                        q_info = decision.get("quota_info", {})
                        if q_info.get("just_confirmed"):
                            m_type = "TV Episode" if q_info.get("media_type") == "episode" else "Feature Movie"
                            used = q_info.get("used", 1)
                            max_val = q_info.get("max", 2)
                            sub = f"Daily Quota: {m_type} {used}/{max_val} started"
                            apple_script = (
                                f"display notification {applescript_string(title, 40)} "
                                f"with title {applescript_string('Mindful Entertainment 🎬')} "
                                f"subtitle {applescript_string(sub, 80)}"
                            )
                            subprocess.run(["osascript", "-e", apple_script], capture_output=True)
                        record_allowed_exception(domain, title, reason)
                elif decision.get("category") == "entertainment_browse":
                    if url != last_intercepted_url:
                        last_intercepted_url = url

            time.sleep(0.8)
        except Exception as exc:
            print(f"[Watcher error] {exc}", file=sys.stderr)
            time.sleep(1.0)

class FocusHTTPHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with stats_lock:
                act = stats.get("active_profile", DEFAULT_PROFILE_ID)
                stats_copy = dict(stats)
                stats_copy["active_profile"] = act
                stats_copy["profile_details"] = serialize_profile(get_profile(act))
                stats_copy["quota"] = get_quota_summary()
                stats_copy["rag"] = get_rag().get_stats()
                data = json.dumps(stats_copy).encode("utf-8")
            self.wfile.write(data)
        elif parsed.path == "/api/history":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with history_lock:
                data = json.dumps(cached_history_data).encode("utf-8")
            self.wfile.write(data)
        elif parsed.path == "/api/profiles":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with stats_lock:
                act = stats.get("active_profile", DEFAULT_PROFILE_ID)
            resp = {
                "active": act,
                "active_profile": serialize_profile(get_profile(act)),
                "profiles": list_profiles()
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif parsed.path == "/api/profile":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            new_prof = qs.get("set", [None])[0]
            if new_prof == "student":
                new_prof = "academic"
            if new_prof and new_prof in PROFILES:
                with stats_lock:
                    stats["active_profile"] = new_prof
                    save_stats(stats)
                threading.Thread(target=refresh_history_cache, daemon=True).start()
                p = get_profile(new_prof)
                p_name = p.get('name', 'Persona')
                p_badge = p.get('badge', '')
                script = (
                    f"display notification {applescript_string(f'Switched focus persona to {p_name}', 120)} "
                    f"with title {applescript_string(f'Focus Persona Active {p_badge}', 80)}"
                )
                subprocess.run(["osascript", "-e", script], capture_output=True)
                resp = {"status": "ok", "active": new_prof, "profile": serialize_profile(p)}
            else:
                with stats_lock:
                    act = stats.get("active_profile", DEFAULT_PROFILE_ID)
                resp = {"active": act, "profile": serialize_profile(get_profile(act))}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif parsed.path == "/api/reset":
            with stats_lock:
                stats["total_intercepted"] = 0
                stats["site_counts"] = {}
                stats["history"] = []
                stats["exceptions_allowed"] = []
                save_stats(stats)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "reset"}')
        elif parsed.path == "/api/quota":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = json.dumps(get_quota_summary()).encode("utf-8")
            self.wfile.write(data)
        elif parsed.path == "/api/quota/reset":
            summary = reset_quota_today()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(summary).encode("utf-8"))
        elif parsed.path == "/api/quota/set":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            max_ep = qs.get("episodes", [2])[0]
            max_mov = qs.get("movies", [1])[0]
            try:
                summary = set_quota_limits(int(max_ep), int(max_mov))
            except Exception as e:
                summary = {"error": str(e)}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(summary).encode("utf-8"))
        elif parsed.path == "/api/rag":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = json.dumps(get_rag().get_stats()).encode("utf-8")
            self.wfile.write(data)
        elif parsed.path == "/api/rag/query":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            q_title = qs.get("title", ["Steve Brunton: Physics-Informed Neural Networks"])[0]
            q_url = qs.get("url", ["https://www.youtube.com/watch?v=sample"])[0]
            with stats_lock:
                prof = stats.get("active_profile", DEFAULT_PROFILE_ID)
            res = get_rag().retrieve(q_url, q_title, profile_id=prof)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
        elif parsed.path == "/api/rag/feedback":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            title = qs.get("title", [""])[0]
            domain = qs.get("domain", [""])[0]
            action = qs.get("action", ["ALLOW"])[0]
            reason = qs.get("reason", ["User override"])[0]
            resp = get_rag().record_feedback(title, domain, action, reason, user_override=True)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif parsed.path == "/api/rag/goal/add":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            topic = qs.get("topic", [""])[0]
            kws = [k.strip() for k in qs.get("keywords", [""])[0].split(",") if k.strip()]
            cat = qs.get("category", ["academic"])[0]
            if topic:
                resp = get_rag().add_user_goal(topic, kws, cat)
            else:
                resp = {"error": "Missing topic"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif parsed.path == "/api/rag/goal/delete":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            gid = qs.get("id", [None])[0]
            if gid:
                resp = get_rag().delete_user_goal(int(gid))
            else:
                resp = {"error": "Missing id"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            try:
                with open(DASHBOARD_FILE, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Invalid JSON: {exc}".encode("utf-8"))
            return

        if parsed.path == "/api/reset":
            with stats_lock:
                stats["total_intercepted"] = 0
                stats["site_counts"] = {}
                stats["history"] = []
                stats["exceptions_allowed"] = []
                save_stats(stats)
            self.send_response(204)
            self.end_headers()
            return
        if parsed.path == "/api/quota/reset":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(reset_quota_today()).encode("utf-8"))
            return
        if parsed.path == "/api/rag/goal/delete":
            try:
                goal_id = int(body.get("id"))
                resp = get_rag().delete_user_goal(goal_id)
            except (TypeError, ValueError) as exc:
                resp = {"error": f"Invalid goal id: {exc}"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        if parsed.path == "/api/profile":
            try:
                new_prof = body.get("profile")
                if new_prof == "student":
                    new_prof = "academic"
                if new_prof in PROFILES:
                    with stats_lock:
                        stats["active_profile"] = new_prof
                        save_stats(stats)
                    threading.Thread(target=refresh_history_cache, daemon=True).start()
                    p = get_profile(new_prof)
                    p_name = p.get('name', 'Persona')
                    p_badge = p.get('badge', '')
                    script = (
                        f"display notification {applescript_string(f'Switched focus persona to {p_name}', 120)} "
                        f"with title {applescript_string(f'Focus Persona Active {p_badge}', 80)}"
                    )
                    subprocess.run(["osascript", "-e", script], capture_output=True)
                    resp = {"status": "ok", "active": new_prof, "profile": serialize_profile(p)}
                else:
                    resp = {"error": f"Unknown profile: {new_prof}"}
            except Exception as e:
                resp = {"error": str(e)}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif parsed.path == "/api/quota/set":
            try:
                max_ep = body.get("episodes", 2)
                max_mov = body.get("movies", 1)
                resp = set_quota_limits(int(max_ep), int(max_mov))
            except Exception as e:
                resp = {"error": str(e)}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif parsed.path == "/api/quota/reset":
            resp = reset_quota_today()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif parsed.path == "/api/rag/feedback":
            try:
                title = body.get("title", "")
                domain = body.get("domain", "")
                action = body.get("action", "ALLOW")
                reason = body.get("reason", "User override")
                resp = get_rag().record_feedback(title, domain, action, reason, user_override=True)
            except Exception as e:
                resp = {"error": str(e)}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif parsed.path == "/api/rag/goal/add":
            try:
                topic = body.get("topic", "")
                keywords = body.get("keywords", [])
                category = body.get("category", "academic")
                resp = get_rag().add_user_goal(topic, keywords, category)
            except Exception as e:
                resp = {"error": str(e)}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

def run_server():
    # Initial history population
    refresh_history_cache()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), FocusHTTPHandler)
    print(f"🚀 Focus Dashboard live at: http://localhost:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    pid_file = os.path.join(BASE_DIR, "focus.pid")
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    def handle_exit(sig, frame):
        print("\nStopping Focus daemon...")
        if os.path.exists(pid_file):
            os.remove(pid_file)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    watcher_thread = threading.Thread(target=tab_watcher_loop, daemon=True)
    watcher_thread.start()

    try:
        run_server()
    except KeyboardInterrupt:
        handle_exit(None, None)
