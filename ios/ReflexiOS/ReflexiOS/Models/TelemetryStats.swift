import Foundation

public struct TelemetryStats: Codable {
    public var totalIntercepted: Int
    public var siteCounts: [String: Int]
    public var activeProfile: String
    public var profileDetails: FocusProfile?
    public var quota: QuotaSummary?
    
    enum CodingKeys: String, CodingKey {
        case totalIntercepted = "total_intercepted"
        case siteCounts = "site_counts"
        case activeProfile = "active_profile"
        case profileDetails = "profile_details"
        case quota
    }
    
    public init(
        totalIntercepted: Int = 0,
        siteCounts: [String: Int] = [:],
        activeProfile: String = "academic",
        profileDetails: FocusProfile? = .student,
        quota: QuotaSummary? = .sample
    ) {
        self.totalIntercepted = totalIntercepted
        self.siteCounts = siteCounts
        self.activeProfile = activeProfile
        self.profileDetails = profileDetails
        self.quota = quota
    }
    
    public static let sample = TelemetryStats(
        totalIntercepted: 14,
        siteCounts: [
            "youtube.com": 9,
            "netflix.com": 3,
            "instagram.com": 2
        ],
        activeProfile: "academic",
        profileDetails: .student,
        quota: .sample
    )
}
