import Foundation
import SwiftUI
import Combine

public enum ConnectionState: String {
    case connected = "SYNCED"
    case connecting = "CONNECTING"
    case offlineStandalone = "STANDALONE"
    case error = "UNREACHABLE"
    
    public var statusIndicator: String {
        switch self {
        case .connected: return "[LIVE // OK]"
        case .connecting: return "[CONNECTING...]"
        case .offlineStandalone: return "[LOCAL // OFFLINE]"
        case .error: return "[NO SIGNAL]"
        }
    }
}

@MainActor
public final class ReflexClient: ObservableObject {
    @Published public var state: ConnectionState = .offlineStandalone
    @Published public var serverHost: String {
        didSet {
            UserDefaults.standard.set(serverHost, forKey: "reflex_server_host")
        }
    }
    @Published public var serverPort: Int {
        didSet {
            UserDefaults.standard.set(serverPort, forKey: "reflex_server_port")
        }
    }
    @Published public var forceStandalone: Bool {
        didSet {
            UserDefaults.standard.set(forceStandalone, forKey: "reflex_force_standalone")
            if forceStandalone {
                state = .offlineStandalone
            }
        }
    }
    
    @Published public var activeProfile: FocusProfile = .student
    @Published public var allProfiles: [FocusProfile] = FocusProfile.defaultProfiles
    @Published public var quota: QuotaSummary = .sample
    @Published public var stats: TelemetryStats = .sample
    @Published public var lastSyncTime: Date?
    @Published public var errorMessage: String?
    
    private var timer: AnyCancellable?
    private let session: URLSession
    private var isBackgrounded: Bool = false
    private var consecutiveFailures: Int = 0
    private var currentInterval: TimeInterval = 3.0
    
    public init() {
        let savedHost = UserDefaults.standard.string(forKey: "reflex_server_host") ?? "127.0.0.1"
        let savedPort = UserDefaults.standard.integer(forKey: "reflex_server_port")
        let savedStandalone = UserDefaults.standard.bool(forKey: "reflex_force_standalone")
        
        self.serverHost = savedHost.isEmpty ? "127.0.0.1" : savedHost
        self.serverPort = savedPort > 0 ? savedPort : 5050
        self.forceStandalone = savedStandalone
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 3.0
        config.timeoutIntervalForResource = 4.0
        self.session = URLSession(configuration: config)
        
        // Load initial local state
        loadLocalState()
        
        // Configure adaptive power-saving lifecycle observers
        setupLifecycleObservers()
        
        // Start polling
        startPolling(interval: 3.0)
    }
    
    public var baseURLString: String {
        "http://\(serverHost):\(serverPort)"
    }
    
    public func startPolling(interval: TimeInterval = 3.0) {
        currentInterval = interval
        timer?.cancel()
        timer = Timer.publish(every: interval, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                Task { [weak self] in
                    await self?.pollServer()
                }
            }
        Task {
            await pollServer()
        }
    }
    
    private func setupLifecycleObservers() {
        #if canImport(UIKit)
        NotificationCenter.default.addObserver(
            forName: UIApplication.didEnterBackgroundNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.isBackgrounded = true
            // Save battery: throttle from 3s to 30s in background
            self?.startPolling(interval: 30.0)
        }
        
        NotificationCenter.default.addObserver(
            forName: UIApplication.didBecomeActiveNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.isBackgrounded = false
            self?.consecutiveFailures = 0
            // Instant response: resume 3s polling in foreground
            self?.startPolling(interval: 3.0)
        }
        #endif
    }
    
    public func stopPolling() {
        timer?.cancel()
        timer = nil
    }
    
    public func pollServer() async {
        if forceStandalone {
            state = .offlineStandalone
            return
        }
        
        guard let statsURL = URL(string: "\(baseURLString)/api/stats") else { return }
        
        do {
            let (data, response) = try await session.data(from: statsURL)
            guard let httpResp = response as? HTTPURLResponse, httpResp.statusCode == 200 else {
                handleOfflineFallback("Invalid HTTP status")
                return
            }
            
            let decoder = JSONDecoder()
            if let decodedStats = try? decoder.decode(TelemetryStats.self, from: data) {
                self.stats = decodedStats
                if let q = decodedStats.quota {
                    self.quota = q
                }
                if let p = decodedStats.profileDetails {
                    self.activeProfile = p
                }
            }
            
            self.state = .connected
            self.lastSyncTime = Date()
            self.errorMessage = nil
            self.consecutiveFailures = 0
            
            // Also fetch profiles list if empty
            if self.allProfiles.isEmpty {
                await fetchProfiles()
            }
        } catch {
            handleOfflineFallback(error.localizedDescription)
        }
    }
    
    public func fetchProfiles() async {
        guard let url = URL(string: "\(baseURLString)/api/profiles") else { return }
        do {
            let (data, response) = try await session.data(from: url)
            guard let httpResp = response as? HTTPURLResponse, httpResp.statusCode == 200 else { return }
            
            struct ProfilesResp: Codable {
                let active: String
                let activeProfile: FocusProfile?
                let profiles: [FocusProfile]
                
                enum CodingKeys: String, CodingKey {
                    case active
                    case activeProfile = "active_profile"
                    case profiles
                }
            }
            
            let resp = try JSONDecoder().decode(ProfilesResp.self, from: data)
            self.allProfiles = resp.profiles
            if let act = resp.activeProfile {
                self.activeProfile = act
            }
        } catch {
            // Keep existing profiles
        }
    }
    
    public func switchProfile(to profile: FocusProfile) async {
        self.activeProfile = profile
        saveLocalActiveProfile(profile.id)
        
        if forceStandalone || state != .connected {
            return
        }
        
        guard let url = URL(string: "\(baseURLString)/api/profile?set=\(profile.id)") else { return }
        _ = try? await session.data(from: url)
    }
    
    public func resetQuota() async {
        if forceStandalone || state != .connected {
            self.quota.episodesUsed = 0
            self.quota.moviesUsed = 0
            self.quota.episodesRemaining = self.quota.episodesMax
            self.quota.moviesRemaining = self.quota.moviesMax
            self.quota.episodesList = []
            self.quota.moviesList = []
            return
        }
        
        guard let url = URL(string: "\(baseURLString)/api/quota/reset") else { return }
        do {
            let (data, _) = try await session.data(from: url)
            if let updated = try? JSONDecoder().decode(QuotaSummary.self, from: data) {
                self.quota = updated
            }
        } catch {
            // Local fallback
            self.quota.episodesUsed = 0
            self.quota.moviesUsed = 0
        }
    }
    
    public func recordLocalEntertainmentConsumed(type: String, title: String) {
        let item = WatchedItem(
            title: title,
            timestamp: DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .short),
            mediaType: type
        )
        if type == "series" {
            self.quota.episodesUsed += 1
            self.quota.episodesRemaining = max(0, self.quota.episodesMax - self.quota.episodesUsed)
            self.quota.episodesList.insert(item, at: 0)
        } else {
            self.quota.moviesUsed += 1
            self.quota.moviesRemaining = max(0, self.quota.moviesMax - self.quota.moviesUsed)
            self.quota.moviesList.insert(item, at: 0)
        }
    }
    
    private func handleOfflineFallback(_ reason: String) {
        consecutiveFailures += 1
        if state == .connected {
            // Just disconnected
            self.errorMessage = reason
        }
        self.state = .offlineStandalone
        
        // Adaptive power saving: if device is in pocket and server is unreachable, back off to 60s
        if isBackgrounded && consecutiveFailures >= 2 && currentInterval < 60.0 {
            startPolling(interval: 60.0)
        }
    }
    
    private func loadLocalState() {
        let savedProfId = UserDefaults.standard.string(forKey: "reflex_active_profile") ?? "academic"
        if let p = FocusProfile.defaultProfiles.first(where: { $0.id == savedProfId }) {
            self.activeProfile = p
        }
    }
    
    private func saveLocalActiveProfile(_ id: String) {
        UserDefaults.standard.set(id, forKey: "reflex_active_profile")
    }
}
