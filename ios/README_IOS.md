# REFLEX iOS // PERSONAL SIDELOADING GUIDE
```
   ____  _____ _____ _     _______  __     _ ____  ____  
  |  _ \| ____|  ___| |   | ____\ \/ /    (_)  _ \/ ___| 
  | |_) |  _| | |_  | |   |  _|  \  /     | | | | \___ \ 
  |  _ <| |___|  _| | |___| |___ /  \     | | |_| |___) |
  |_| \_\_____|_|   |_____|_____/_/\_\    |_|____/|____/ 
  
  [HARDWARE-ACCELERATED DUAL SHIELD // MAC + iOS PARALLEL]
  [AESTHETIC: ASCII-MAGIC.COM // 432Hz HARMONIC STUDIO]
```

This iOS edition of **Reflex** is specifically architected for **personal sideloading** without going through the Apple App Store. You retain 100% data sovereignty, zero telemetry tracking, and zero recurring fees.

---

## ⚡ ARCHITECTURE OVERVIEW

The iOS app operates in two synchronized modes:

1. **LIVE SYNC MODE (Connected to Mac via Local Wi-Fi):**
   - Polls your Mac's Reflex background daemon (`focus_daemon.py`) at `http://<mac-ip>:5050`.
   - Displays real-time intercepted distraction count, active focus persona, and synchronized daily entertainment quota (`[ █ ░ ]`).
   - Tapping persona pills on iOS immediately updates the active mode on your Mac.
   - Resetting quotas or logging media on iOS reflects instantly on your Mac dashboard.

2. **STANDALONE FOCUS STUDIO (Offline On-Device):**
   - When you are away from your Mac, the app functions as an autonomous focus studio:
     - 60 FPS interactive ASCII touch wave canvas (perturb resonance with your finger).
     - 25-minute Pomodoro focus sprint engine with Space Mono glowing typography.
     - Pure 432Hz Tibetan singing bowl harmonic synthesis via `AVAudioEngine`.
     - Offline entertainment quota tracker (`[ █ ░ ] 1/2 EPISODES`, `[ ░ ] 0/1 MOVIES`).
     - Persona quick portals (Canvas LMS, Scholar, Overleaf, arXiv, GitHub, Claude, etc.).

---

## ⏱️ WILL IT BE ALIVE 24/7?

There are two distinct parts to keeping an iOS app alive 24/7:
1. **Runtime Execution (Process staying awake when the phone is locked)**
2. **Installation Expiry (Preventing Apple's 7-day sideloading certificate limit)**

Here is exactly how both are solved:

### 1. Runtime 24/7: Background Sentinel & Socket Heartbeat
Normal iOS apps get suspended by Apple within 30 seconds of locking your phone or switching apps.
Reflex overcomes this using:
- **`UIBackgroundModes: ["audio", "fetch", "processing"]`**: Apple's designated low-power background capability.
- **24/7 Background Sentinel**: Enabled by default in the `[CFG]` sheet. It maintains an ultra-low-power ambient audio session (`.playback` category with `mixWithOthers`).
- **Result**: iOS **never terminates or freezes** Reflex. It continuously polls your Mac daemon, tracks entertainment quotas, and sounds sprint alerts even when the iPhone screen is completely locked in your pocket.

### 2. Installation 24/7: Staying Installed Forever Without Expiring
When sideloading with a **free personal Apple ID**, Apple signs the app with a 7-day expiration profile. Here is how to keep it alive permanently:

| Method | Setup Effort | Computer Needed After Setup? | Longevity |
| :--- | :--- | :--- | :--- |
| **SideStore (Recommended)** | 5 mins | ❌ **Zero (100% on-phone auto-renewal)** | **Permanent (24/7/365)** |
| **AltStore (AltServer)** | 2 mins | Automatic when near home Wi-Fi | **Permanent (24/7/365)** |
| **Xcode Wireless Sync** | 1 click | Automatic when Mac is nearby | **Permanent (24/7/365)** |
| **Apple Dev Account** | Paid ($99/yr) | ❌ None | **1 Year without renewal** |

#### Recommended: SideStore (Wire-Free On-Device Auto-Renewal)
1. Install [SideStore](https://sidestore.io) on your iPhone.
2. SideStore creates an internal local WireGuard loopback VPN directly on your iPhone.
3. Every night while your iPhone charges on Wi-Fi, SideStore automatically re-signs Reflex directly on your device.
4. **You never have to plug into a Mac again — it stays alive 24/7/365.**

---

## 🚀 METHOD 1: 1-CLICK XCODE SIDELOADING (RECOMMENDED)

You can install Reflex directly onto your iPhone in under 2 minutes using your standard personal Apple ID.

### Step 1: Open the Project in Xcode
Double-click `ReflexiOS.xcodeproj`:
```bash
open ios/ReflexiOS/ReflexiOS.xcodeproj
```

### Step 2: Plug in your iPhone
- Connect your iPhone to your Mac using a USB-C or Lightning cable.
- Unlock your iPhone and tap **"Trust This Computer"** if prompted.

### Step 3: Configure Personal Free Signing
1. In Xcode's left sidebar (Project Navigator), click the top-level **`ReflexiOS`** blueprint icon.
2. Select the **`ReflexiOS`** target under Targets.
3. Select the **Signing & Capabilities** tab.
4. Ensure **"Automatically manage signing"** is checked.
5. In the **Team** dropdown:
   - Select your name: `Your Name (Personal Team)`.
   - *If no team appears:* Click **"Add an Account..."**, enter your regular free Apple ID and password, and close the window. Then select your Personal Team.
6. In **Bundle Identifier**, if Xcode displays a red conflict warning, simply change `com.personal.reflex` to something unique like `com.yourname.reflex`.

### Step 4: Run onto your iPhone
1. In Xcode's top toolbar, click the device dropdown (next to the ▶ Play button).
2. Select your connected iPhone (e.g., `Mani's iPhone`).
3. Press **`Cmd + R`** (or click the ▶ **Play** button).
4. Xcode compiles the Swift code and copies the app directly onto your phone!

### Step 5: Trust the Certificate on your iPhone (First Time Only)
When you first tap the Reflex icon on your iPhone home screen, iOS may show: *"Untrusted Developer"*.
1. On your iPhone, open **Settings**.
2. Navigate to **General > VPN & Device Management** (or *Profiles & Device Management*).
3. Under **Developer App**, tap your Apple ID email.
4. Tap **Trust "[Your Apple ID]"** and confirm.
5. Launch **Reflex**!

> **Note on Free Personal Apple IDs:** Free Apple IDs sign sideloaded apps for 7 days. If you keep your iPhone connected to Wi-Fi on the same network as your Mac with Xcode open, Xcode automatically renews the profile wirelessly.

---

## 📱 METHOD 2: SWIFT PLAYGROUNDS (NO 15GB XCODE NEEDED)

If you do not want to install full Xcode (15GB), you can use Apple's free **Swift Playgrounds** app (available on the Mac App Store and iPad App Store):
1. Download **Swift Playgrounds** from the Mac App Store (~500MB).
2. Drag the `ReflexiOS` directory into Swift Playgrounds.
3. Connect your iPhone and click **Install App**.

---

## ☁️ METHOD 3: WIRELESS ALTSTORE / SIDESTORE / SIDELOADLY

If you use AltStore, SideStore, or Sideloadly on your device:
1. Build the `.ipa` using Xcode: **Product > Archive > Distribute App > Development**.
2. Send the `.ipa` to your iPhone via AirDrop or iCloud Drive.
3. Open with **AltStore** / **SideStore** to install and refresh automatically over local Wi-Fi.

---

## 🔗 CONNECTING REFLEX iOS TO YOUR MAC DAEMON

Once the app is running on your iPhone:

1. **Ensure your Mac daemon is running:**
   ```bash
   cd /Users/jakkasaisrinivasamanideep/Documents/FocusRedirect
   ./focus.sh start
   ```

2. **Find your Mac's Local IP Address:**
   Run this in Terminal:
   ```bash
   ipconfig getifaddr en0
   ```
   *(e.g., `192.168.1.142`)*

3. **Configure the iPhone App:**
   - On your iPhone, open **Reflex**.
   - Tap the **`[CFG]`** button in the top right corner.
   - Enter your Mac's IP (e.g., `192.168.1.142`) into the **IP HOST** field.
   - Leave port as `5050`.
   - Tap **`[TEST CONNECTION]`**.
   - You will hear the 432Hz bowl chime and see **`PING OK [200]`**.
   - Tap **`[SAVE]`**.

Your iPhone and Mac are now paired in real-time! The status pill will display **`[LIVE // OK]`** in emerald green.

---

## 🎛️ FILE STRUCTURE

```
ios/
├── README_IOS.md                     <- This installation and architecture guide
└── ReflexiOS/
    ├── Package.swift                 <- Swift Package Manager manifest
    ├── ReflexiOS.xcodeproj/          <- Ready-to-open Xcode project
    │   └── project.pbxproj
    └── ReflexiOS/
        ├── ReflexiOSApp.swift        <- @main SwiftUI App entry point
        ├── Info.plist                <- Local network permissions & dark status bar
        ├── Assets.xcassets/          <- High-res 1024x1024 [RX] ASCII App Icon
        ├── Models/
        │   ├── FocusProfile.swift    <- Student, Dev, Founder, Studio, General, Monk
        │   ├── QuotaSummary.swift    <- Entertainment Quota & media logs model
        │   └── TelemetryStats.swift  <- Network telemetry & interception stats
        ├── Services/
        │   ├── ReflexClient.swift    <- URLSession background polling & offline engine
        │   ├── AudioHapticsService.swift <- 432Hz Tibetan bowl synthesis & tactile haptics
        │   └── ScreenTimeManager.swift <- Native FamilyControls & ManagedSettings bridge
        └── Views/
            ├── ASCIICanvasView.swift <- 60 FPS interactive ASCII harmonic wave canvas
            ├── ContentView.swift     <- Main dashboard with side rails & tab navigation
            ├── QuotaCardView.swift   <- Monospace capsule meters [ █ ░ ]
            ├── StopwatchView.swift   <- 25m focus sprint countdown & 432Hz bell
            ├── PersonaSelectorView.swift <- Persona pills & quick launch portals
            └── SettingsSheetView.swift   <- Bridge host, port & standalone configuration
```

---

*Reflex Protocol // Self-Hosted Dual Shield // Build 2.4.0*
