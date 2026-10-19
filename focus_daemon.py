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
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

from decision_engine import evaluate_tab
from history_reader import analyze_history

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
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "total_intercepted": 0,
        "site_counts": {},
        "history": [],
        "exceptions_allowed": []
    }

def save_stats(data):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[Error saving stats] {e}", file=sys.stderr)

stats = load_stats()

# Cached history analysis (refreshed periodically)
cached_history_data = {}
history_lock = threading.Lock()

def refresh_history_cache():
    global cached_history_data
    try:
        data = analyze_history(limit=400)
        with history_lock:
            cached_history_data = data
    except Exception as e:
        print(f"[History cache error] {e}", file=sys.stderr)

def notify_user(domain, reason=""):
    subtitle = reason if reason else "Entertainment Intercepted"
    apple_script = f'''
    display notification "Redirected from {domain} to your Focus Zone." with title "Focus Mode Active 🎯" subtitle "{subtitle[:35]}"
    '''
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

                decision = evaluate_tab(url, title, recent_trajectory=trajectory)
                action = decision.get("action")
                domain = decision.get("domain", "")

                if action == "REDIRECT":
                    if url != last_intercepted_url or (now - last_intercept_time) > 2.0:
                        last_intercepted_url = url
                        last_intercept_time = now
                        redirect_active_tab(browser, REDIRECT_URL)
                        record_intercept(domain, decision.get("reason", "Entertainment"), title)
                elif decision.get("category") in ("educational_exception", "podcast_exception"):
                    # Record exception once per session
                    if url != last_intercepted_url:
                        last_intercepted_url = url
                        label = "Podcast" if decision.get("category") == "podcast_exception" else "Educational"
                        record_allowed_exception(domain, title, decision.get("reason", label))

            time.sleep(0.8)
        except Exception:
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
                data = json.dumps(stats).encode("utf-8")
            self.wfile.write(data)
        elif parsed.path == "/api/history":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with history_lock:
                data = json.dumps(cached_history_data).encode("utf-8")
            self.wfile.write(data)
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

    def log_message(self, format, *args):
        return

def run_server():
    # Initial history population
    refresh_history_cache()
    server = HTTPServer(("127.0.0.1", PORT), FocusHTTPHandler)
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
