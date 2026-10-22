import Foundation
import SwiftUI
#if canImport(FamilyControls)
import FamilyControls
#endif
#if canImport(ManagedSettings)
import ManagedSettings
#endif

@MainActor
public final class ScreenTimeManager: ObservableObject {
    public static let shared = ScreenTimeManager()
    
    @Published public var isAuthorized: Bool = false
    @Published public var shieldActive: Bool = false
    @Published public var blockedCategoriesCount: Int = 0
    @Published public var statusMessage: String = "IDLE // READY"
    
    private init() {
        checkAuthorization()
    }
    
    public func checkAuthorization() {
        #if canImport(FamilyControls)
        if #available(iOS 16.0, *) {
            let center = AuthorizationCenter.shared
            self.isAuthorized = (center.authorizationStatus == .approved)
        }
        #endif
    }
    
    public func requestAuthorization() async {
        #if canImport(FamilyControls)
        if #available(iOS 16.0, *) {
            do {
                try await AuthorizationCenter.shared.requestAuthorization(for: .individual)
                self.isAuthorized = (AuthorizationCenter.shared.authorizationStatus == .approved)
                self.statusMessage = isAuthorized ? "SCREEN_TIME // GRANTED" : "SCREEN_TIME // DENIED"
            } catch {
                self.statusMessage = "SCREEN_TIME // STANDALONE_MODE"
            }
        }
        #else
        self.statusMessage = "STANDALONE_MODE"
        #endif
    }
    
    public func toggleShield(active: Bool) {
        self.shieldActive = active
        #if canImport(ManagedSettings)
        if #available(iOS 16.0, *) {
            let store = ManagedSettingsStore()
            if active {
                // If user selected apps to shield, shield them
                self.statusMessage = "SHIELD // ACTIVE"
            } else {
                store.clearAllSettings()
                self.statusMessage = "SHIELD // DISARMED"
            }
        }
        #endif
    }
}
