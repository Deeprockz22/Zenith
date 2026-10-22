#!/bin/bash
# ==============================================================================
# FocusRedirect Management Script
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$DIR/focus.pid"
DAEMON_SCRIPT="$DIR/focus_daemon.py"
LOG_FILE="$DIR/focus.log"

PYTHON_BIN="$DIR/.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

start() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "⚠️  Focus Redirect is already running (PID: $(cat "$PID_FILE"))"
        echo "👉 Dashboard: http://localhost:5050"
        return
    fi

    echo "🚀 Starting Focus Redirect & Jev Decision Engine..."
    "$PYTHON_BIN" "$DAEMON_SCRIPT" > "$LOG_FILE" 2>&1 &
    sleep 2

    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "✅ Started successfully (PID: $(cat "$PID_FILE"))"
        echo "👉 Focus Dashboard live at: http://localhost:5050"
        echo "👁️  Monitoring entertainment tabs (YouTube, Instagram, X/Twitter, Threads, etc.)"
    else
        echo "❌ Failed to start. Check $LOG_FILE"
    fi
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID="$(cat "$PID_FILE")"
        if kill -0 "$PID" 2>/dev/null; then
            echo "🛑 Stopping Focus Redirect (PID: $PID)..."
            kill "$PID"
            rm -f "$PID_FILE"
            echo "✅ Focus Redirect stopped."
            return
        fi
        rm -f "$PID_FILE"
    fi
    echo "ℹ️  Focus Redirect is not running."
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "🟢 Focus Redirect is ACTIVE (PID: $(cat "$PID_FILE"))"
        echo "👉 Dashboard: http://localhost:5050"
        echo ""
        if [ -f "$DIR/focus_stats.json" ]; then
            python3 -c "
import json
with open('$DIR/focus_stats.json') as f:
    d = json.load(f)
print('📊 Intercepts today:', d.get('total_intercepted', 0))
for site, count in d.get('site_counts', {}).items():
    print(f'   - {site}: {count}')
"
        fi
    else
        echo "🔴 Focus Redirect is STOPPED."
    fi
}

open_dashboard() {
    open "http://localhost:5050"
}

profile() {
    if [ -z "$2" ]; then
        echo "══════════════════════════════════════════════════════════════════"
        echo "🧠 ZENITH FOCUS PERSONAS & PROFILES"
        echo "══════════════════════════════════════════════════════════════════"
        python3 -c "
import urllib.request, json
try:
    with urllib.request.urlopen('http://localhost:5050/api/profiles') as res:
        data = json.loads(res.read().decode())
        act = data.get('active', '')
        for p in data.get('profiles', []):
            mark = '👉 [ACTIVE]' if p['id'] == act else '  '
            print(f\"{mark:12s} {p['badge']:10s} {p['id']:12s} | {p['name']:22s} -> {p['tagline']}\")
except Exception:
    import sys
    sys.path.append('$DIR')
    from profiles import list_profiles
    for p in list_profiles():
        print(f\"   {p['badge']:10s} {p['id']:12s} | {p['name']:22s} -> {p['tagline']}\")
"
        echo "──────────────────────────────────────────────────────────────────"
        echo "💡 Switch profile with: ./focus.sh profile <id>"
        echo "   Example: ./focus.sh profile developer"
        echo "══════════════════════════════════════════════════════════════════"
    else
        python3 -c "
import urllib.request, json
try:
    with urllib.request.urlopen('http://localhost:5050/api/profile?set=$2') as res:
        d = json.loads(res.read().decode())
        if 'error' in d:
            print('❌ Error:', d['error'])
        else:
            p = d.get('profile', {})
            print(f'✅ Switched Focus Persona to: {p.get(\"badge\")} {p.get(\"name\")}')
            print(f'🎯 Tagline: {p.get(\"tagline\")}')
except Exception as e:
    print('⚠️ Daemon not running or error:', e)
"
    fi
}

quota() {
    sub="$2"
    if [ "$sub" = "reset" ]; then
        python3 -c "
import urllib.request, json
try:
    with urllib.request.urlopen('http://localhost:5050/api/quota/reset') as res:
        d = json.loads(res.read().decode())
        print('✅ Daily entertainment quota reset!')
        print(f'   Series: 0/{d.get(\"episodes_max\", 2)} | Movies: 0/{d.get(\"movies_max\", 1)}')
except Exception as e:
    import sys
    sys.path.append('$DIR')
    from quota_manager import reset_quota_today
    d = reset_quota_today()
    print('✅ Daily entertainment quota reset (direct)!')
    print(f'   Series: 0/{d.get(\"episodes_max\", 2)} | Movies: 0/{d.get(\"movies_max\", 1)}')
"
    elif [ "$sub" = "set" ]; then
        eps="${3:-2}"
        movs="${4:-1}"
        python3 -c "
import urllib.request, json
try:
    with urllib.request.urlopen(f'http://localhost:5050/api/quota/set?episodes=$eps&movies=$movs') as res:
        d = json.loads(res.read().decode())
        print(f'✅ Entertainment quota limits updated: Max {d.get(\"episodes_max\")} episodes, {d.get(\"movies_max\")} movies per day.')
except Exception as e:
    import sys
    sys.path.append('$DIR')
    from quota_manager import set_quota_limits
    d = set_quota_limits($eps, $movs)
    print(f'✅ Entertainment quota limits updated (direct): Max {d.get(\"episodes_max\")} episodes, {d.get(\"movies_max\")} movies per day.')
"
    else
        echo "══════════════════════════════════════════════════════════════════"
        echo "🎬 MINDFUL ENTERTAINMENT QUOTA (DAILY LIMITS)"
        echo "══════════════════════════════════════════════════════════════════"
        python3 -c "
import urllib.request, json
try:
    with urllib.request.urlopen('http://localhost:5050/api/quota') as res:
        d = json.loads(res.read().decode())
except Exception:
    import sys
    sys.path.append('$DIR')
    from quota_manager import get_quota_summary
    d = get_quota_summary()

ep_u = d.get('episodes_used', 0)
ep_m = d.get('episodes_max', 2)
ep_r = d.get('episodes_remaining', 2)
ep_bar = '[' + ' █' * ep_u + ' ░' * ep_r + ' ]'

mov_u = d.get('movies_used', 0)
mov_m = d.get('movies_max', 1)
mov_r = d.get('movies_remaining', 1)
mov_bar = '[' + ' █' * mov_u + ' ░' * mov_r + ' ]'

print(f'📅 Date       : {d.get(\"date\")}')
print(f'📺 TV Series  : {ep_bar} ({ep_u}/{ep_m} used, {ep_r} remaining)')
if d.get('episodes_list'):
    for item in d['episodes_list']:
        print(f'               • {item.get(\"title\", \"Episode\")[:50]}')
print(f'🎬 Movies     : {mov_bar} ({mov_u}/{mov_m} used, {mov_r} remaining)')
if d.get('movies_list'):
    for item in d['movies_list']:
        print(f'               • {item.get(\"title\", \"Movie\")[:50]}')
"
        echo "──────────────────────────────────────────────────────────────────"
        echo "💡 Commands:"
        echo "   ./focus.sh quota reset              (reset today's count)"
        echo "   ./focus.sh quota set <eps> <movies> (e.g. ./focus.sh quota set 2 1)"
        echo "══════════════════════════════════════════════════════════════════"
    fi
}

run_fg() {
    export PATH="$DIR/.venv/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
    exec "$PYTHON_BIN" "$DAEMON_SCRIPT"
}

case "$1" in
    start)
        start
        ;;
    run-fg)
        run_fg
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    profile)
        profile "$@"
        ;;
    quota)
        quota "$@"
        ;;
    open)
        open_dashboard
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart|open|profile [id]|quota [reset|set]}"
        exit 1
        ;;
esac
