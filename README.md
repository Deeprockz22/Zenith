# Zenith

```text
                 .                 .
             .       .         .       .
          .      .      .   .      .      .
        .    .       .       .       .    .
       .       .   .    _    .   .       .
        .       .    / / \ \    .       .
          .      .  / /___\ \  .      .
             .     /  _____  \     .
                   /_/     \_\

              Z E N I T H
        a quieter route back to the work
```

> A local macOS tool that notices when browsing is drifting away from your
> work and gives you a deliberate way to return.

[![macOS](https://img.shields.io/badge/platform-macOS%20Apple%20Silicon-black?logo=apple)](https://apple.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Inference](https://img.shields.io/badge/Inference-47.5ms%20(MPS)-emerald)](https://github.com/ikermoel/open-alternative-jev)
[![Architecture](https://img.shields.io/badge/Architecture-Jev%20System%20One-indigo)](https://typesafe.ai)

---

## What it does

Zenith is for the moment when a short break quietly turns into another hour online.
It watches the active browser tab, looks at the page title and URL, and uses your
recent browsing context to decide whether the tab looks useful or distracting.

It is not a blanket website blocker. An educational video on YouTube can still
be allowed, while a Shorts feed, a trending page, or an entertainment binge can
be redirected to a calm focus screen. The decision is local, the dashboard is
served locally, and the user can choose the active focus profile.

The normal mode uses lightweight rules and local retrieval. An optional Jev
worker can provide deeper classification for ambiguous pages, but it runs in a
separate process so the everyday watcher stays small.

```text
       Impulsive Tab Opened (e.g. YouTube / Reddit / Netflix)
                                |
                                v
         [Tier 1: Fast Whitelist] --(GitHub / Canvas / Overleaf)--> ALLOW (<0.1ms)
                                |
                                v
         [Tier 2: Jev System One Neural Decision Layer (~47ms)]
                                |
          +---------------------+---------------------+
          v                                           v
   Intent: study_or_work                     Intent: entertainment
 (e.g. MIT 18.06 Lecture)                   (e.g. Trending Shorts / Ted Lasso)
          |                                           |
          v                                           v
        ALLOW                                  MINDFUL REDIRECT
(Educational Exception)                      (Quiet Zone Sanctuary)
```

---

## Key Capabilities

### Evidence-informed intervention design

Zenith treats distraction support as a **just-in-time adaptive intervention**, not a permanent wall:

* Interventions use changing context (active tab, title, trajectory, profile, and quota) rather than blocking every visit.
* The dashboard keeps control with the user through explicit profiles, goals, quotas, and reset actions.
* Notifications are brief and limited to meaningful state changes so the intervention does not become another attention sink.

These principles are informed by [Nahum-Shani & Murphy, *Just-in-Time Adaptive Interventions: Where Are We Now and What Is Next?* (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13217361/) and [Lukoff, Lyngs & colleagues, *Designing to Support Autonomy and Reduce Psychological Reactance in Digital Self-Control Tools* (2022)](https://ulriklyngs.com/pdfs/lukoff-lyngs-alberts-2022-dscts_for_autonomy.pdf). They are product-design references, not claims that Zenith is a clinical intervention.

### 1. Local Jev System One Decision Engine
* Powered by `open-alternative-jev` (`so1`) running on top of **`Qwen2.5-0.5B-Instruct`**.
* **47.5 ms average warm latency** on Apple Silicon via Metal Performance Shaders (MPS).
* Outputs calibrated typed probabilities (`Choice`, `yes_no`) in a single forward pass without generating text.
* Distinguishes educational study from entertainment doomscrolling based on page context.

### 2. Local Browser History Intelligence
* Natively inspects local SQLite history from **Arc**, **Google Chrome**, **Brave**, and **Microsoft Edge**.
* Discovers your true habit loops:
  * Automatically identifies your top real-world time-sinks.
  * Maps your daily **Peak Distraction Hours** (e.g. 12:00–13:00 lunch reflex or 23:00 late night).
  * Detects **Dopamine Loops** (3+ rapid distraction switches within 15 minutes) and intervenes.

### 3. Tactile Editorial Focus Sanctuary (`dashboard.html`)
* **Zero AI Clutter**: No neon purple mesh blobs, no floating emojis, no generic templates.
* **Editorial Aesthetics**: Designed with **Instrument Serif**, **Plus Jakarta Sans**, and **JetBrains Mono** telemetry.
* **Handcrafted Web Audio Synthesis**:
  * **432 Hz Tibetan singing bowl / Kyoto Rin bell** with physical harmonic modes and a 1.3Hz acoustic beat.
  * **528 Hz Solfeggio tone** on focus sprint completion.
  * Precision camera-dial detent micro-clicks on controls.
* **Grounding Breathing Guide**: 8-second organic inhale/exhale guide ring.
* **Intentional Portals**: 1-click links to GitHub, Notion, ChatGPT, Claude, LeetCode, and study environments.

### 4. macOS Daemon
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

### Memory-efficient mode

Zenith defaults to the lightweight heuristic/RAG path and does **not** load the
500M-parameter Jev model. This keeps the background daemon small and avoids
allocating model weights unless you explicitly need neural classification.

To opt into the larger model for a session:

```bash
FOCUS_ENABLE_JEV_MODEL=1 ./focus.sh run-fg
```

For everyday use, prefer the default mode; use the neural model for evaluation
or experiments where its additional classification quality is worth the memory
cost.

### Isolated JEV and Rust control plane

When JEV is enabled, Zenith keeps the model in `jev_worker.py`, a separate
process. The browser watcher remains lightweight, and the worker can be
terminated independently if model inference is no longer needed.

The optional `rust-daemon/` crate is a dependency-free, release-optimized
control-plane foundation for moving always-on HTTP/health responsibilities out
of Python. It intentionally does not claim to replace macOS browser automation
yet; that surface still depends on AppleScript permissions and remains in the
Python watcher.

```bash
cd rust-daemon
cargo run --release
curl http://127.0.0.1:5051/health
```

The model is configurable with `FOCUS_JEV_MODEL_ID`; use a smaller compatible
checkpoint or a quantized checkpoint supported by the installed `so1` backend
without changing the watcher:

```bash
FOCUS_ENABLE_JEV_MODEL=1 \
FOCUS_JEV_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct \
./focus.sh run-fg
```

If the installed Transformers environment supports bitsandbytes, `FOCUS_JEV_4BIT=1`
or `FOCUS_JEV_8BIT=1` enables weight quantization. On Apple Silicon, float16
may reduce memory on some setups, but should be benchmarked because backend/device
combinations can fail. Unsupported optimized settings automatically fall back to
the backend default where the worker process remains alive.

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

Navigate to **`http://localhost:5050`**.

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
