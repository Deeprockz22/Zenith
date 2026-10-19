# Reflex · 🧠🌿

> **Sub-50ms neural decision layer and mindful focus sanctuary for macOS.**  
> Intercepting impulsive browsing reflexes before dopamine loops take over.

[![macOS](https://img.shields.io/badge/platform-macOS%20Apple%20Silicon-black?logo=apple)](https://apple.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Inference](https://img.shields.io/badge/Inference-47.5ms%20(MPS)-emerald)](https://github.com/ikermoel/open-alternative-jev)
[![Architecture](https://img.shields.io/badge/Architecture-Jev%20System%20One-indigo)](https://typesafe.ai)

---

## The Philosophy

When you get fatigued or hit a wall while working, your brain's **System 1** (instinctive, automatic impulse) takes over: you unconsciously open a new tab and type `youtube.com`, `instagram.com`, `x.com`, or `netflix.com`.

Standard website blockers are dumb: they block everything blindly with harsh 403 error pages, breaking educational research (e.g. blocking an MIT Linear Algebra lecture because it happens to be hosted on YouTube).

**Reflex replaces blind domain blocking with a 3-tier cognitive safety net:**
1. **Reads Active Context**: Evaluates the page title, URL path, and your recent browsing trajectory.
2. **Runs a Sub-50ms Jev "System One" Neural Decision**: Using a local 500M foundation model running on Apple Silicon Metal Performance Shaders (MPS), Reflex makes a typed decision (`Intent`: `study_or_work` vs. `casual_entertainment`).
3. **Offers a Quiet Sanctuary**: Instead of an aggressive error, Reflex guides your tab to a tranquil, tactile pause screen complete with an 8-second breathing circle, live telemetry, and an acoustic 432Hz Tibetan singing bowl synthesis.

```text
       Impulsive Tab Opened (e.g. YouTube / Reddit / Netflix)
                                │
                                ▼
         [Tier 1: Fast Whitelist] ──(GitHub / Canvas / Overleaf)──> ALLOW (<0.1ms)
                                │
                                ▼
         [Tier 2: Jev System One Neural Decision Layer (~47ms)]
                                │
          ┌─────────────────────┴─────────────────────┐
          ▼                                           ▼
   Intent: study_or_work                     Intent: entertainment
 (e.g. MIT 18.06 Lecture)                   (e.g. Trending Shorts / Ted Lasso)
          │                                           │
          ▼                                           ▼
        ALLOW                                  MINDFUL REDIRECT
(Educational Exception)                      (Quiet Zone Sanctuary)
```

---

## Key Capabilities

### ⚡ 1. Local Jev System One Decision Engine
* Powered by `open-alternative-jev` (`so1`) running on top of **`Qwen2.5-0.5B-Instruct`**.
* **47.5 ms average warm latency** on Apple Silicon via Metal Performance Shaders (MPS).
* Outputs calibrated typed probabilities (`Choice`, `yes_no`) in a single forward pass without generating text.
* Distinguishes educational study from entertainment doomscrolling based on page context.

### 📊 2. Local Browser History Intelligence
* Natively inspects local SQLite history from **Arc**, **Google Chrome**, **Brave**, and **Microsoft Edge**.
* Discovers your true habit loops:
  * Automatically identifies your top real-world time-sinks.
  * Maps your daily **Peak Distraction Hours** (e.g. 12:00–13:00 lunch reflex or 23:00 late night).
  * Detects **Dopamine Loops** (3+ rapid distraction switches within 15 minutes) and intervenes.

### 🌿 3. Tactile Editorial Focus Sanctuary (`dashboard.html`)
* **Zero AI Clutter**: No neon purple mesh blobs, no floating emojis, no generic templates.
* **Editorial Aesthetics**: Designed with **Instrument Serif**, **Plus Jakarta Sans**, and **JetBrains Mono** telemetry.
* **Handcrafted Web Audio Synthesis**:
  * **432 Hz Tibetan singing bowl / Kyoto Rin bell** with physical harmonic modes and a 1.3Hz acoustic beat.
  * **528 Hz Solfeggio tone** on focus sprint completion.
  * Precision camera-dial detent micro-clicks on controls.
* **Grounding Breathing Guide**: 8-second organic inhale/exhale guide ring.
* **Intentional Portals**: 1-click links to GitHub, Notion, ChatGPT, Claude, LeetCode, and study environments.

### 🔄 4. Zero-Friction 24/7 macOS Daemon
* Runs silently in the background with near-zero CPU footprint.
* Auto-starts on macOS boot via [`FocusRedirect.app`](FocusRedirect.app) in **Login Items**.
* Integrated safety net in `~/.zshrc`.

---

## Live Benchmark (Apple Silicon)

```text
[ALLOW   ] (jev-system-one) MIT 18.06 Linear Algebra Lecture 1  -> Jev: Educational (75% conf) [47.3ms]
[REDIRECT] (jev-system-one) Craziest Dog Fails Compilation      -> Jev: Entertainment (98% conf) [48.4ms]
[REDIRECT] (jev-system-one) Watch Ted Lasso Season 3 Episode 1  -> Jev: Entertainment (93% conf) [46.7ms]
[ALLOW   ] (fast-whitelist) HeyPuter/puter on github.com        -> Fast Whitelist [<0.1ms]
```

---

## Quickstart

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/Deeprockz22/reflex-mac.git ~/Documents/Reflex
cd ~/Documents/Reflex

# Create virtual environment and install dependencies
uv venv .venv
source .venv/bin/activate
uv pip install -e path/to/open-alternative-jev
```

### 2. Start the Daemon

```bash
./focus.sh start
```

### 3. Open the Sanctuary Dashboard

Navigate to:
👉 **`http://localhost:5050`**

Or run:
```bash
./focus.sh open
```

---

## Commands

```bash
./focus.sh start    # Start the background watcher and local dashboard
./focus.sh status   # View current intercept telemetry and process PID
./focus.sh stop     # Gracefully stop the watcher
./focus.sh open     # Open the Focus Zone in your default browser
./focus.sh restart  # Hot-reload the daemon
```

---

## Monitored Browsers (macOS)
- **Arc Browser**
- **Safari**
- **Google Chrome**
- **Brave Browser**
- **Microsoft Edge**

---

## License

MIT License. Crafted with quiet focus.
