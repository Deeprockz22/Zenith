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
    open)
        open_dashboard
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart|open}"
        exit 1
        ;;
esac
