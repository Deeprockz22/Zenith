import SwiftUI

@main
struct ReflexiOSApp: App {
    init() {
        // Pre-warm audio and haptics
        AudioHapticsService.shared.prepareHaptics()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
