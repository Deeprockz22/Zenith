import SwiftUI

public struct QuotaCardView: View {
    @ObservedObject var client: ReflexClient
    @State private var showingResetConfirm = false
    
    public init(client: ReflexClient) {
        self.client = client
    }
    
    public var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                Text("[ENTERTAINMENT QUOTA // PROTOCOL]")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                
                Spacer()
                
                Text(client.quota.date ?? "TODAY")
                    .font(.system(size: 10, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.4))
            }
            
            // Capsule Meter Cards
            VStack(spacing: 8) {
                // TV Series Quota Card
                quotaMeterRow(
                    title: "SERIES EPISODES",
                    badge: "MAX \(client.quota.episodesMax) / DAY",
                    used: client.quota.episodesUsed,
                    max: client.quota.episodesMax,
                    remaining: client.quota.episodesRemaining,
                    unit: "EP"
                )
                
                // Movies Quota Card
                quotaMeterRow(
                    title: "FEATURE MOVIES",
                    badge: "MAX \(client.quota.moviesMax) / DAY",
                    used: client.quota.moviesUsed,
                    max: client.quota.moviesMax,
                    remaining: client.quota.moviesRemaining,
                    unit: "FILM"
                )
            }
            
            // Consumed List or Clean Slate
            if !client.quota.episodesList.isEmpty || !client.quota.moviesList.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    Text("LOGGED MEDIA TODAY:")
                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                        .foregroundColor(.white.opacity(0.5))
                    
                    ForEach(client.quota.episodesList) { item in
                        HStack(spacing: 6) {
                            Text("[EP]")
                                .font(.system(size: 9, weight: .bold, design: .monospaced))
                                .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                            Text(item.title)
                                .font(.system(size: 10, weight: .regular, design: .monospaced))
                                .foregroundColor(.white.opacity(0.85))
                                .lineLimit(1)
                            Spacer()
                            if let ts = item.timestamp {
                                Text(ts)
                                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.4))
                            }
                        }
                    }
                    
                    ForEach(client.quota.moviesList) { item in
                        HStack(spacing: 6) {
                            Text("[FILM]")
                                .font(.system(size: 9, weight: .bold, design: .monospaced))
                                .foregroundColor(Color(red: 0.95, green: 0.77, blue: 0.2))
                            Text(item.title)
                                .font(.system(size: 10, weight: .regular, design: .monospaced))
                                .foregroundColor(.white.opacity(0.85))
                                .lineLimit(1)
                            Spacer()
                            if let ts = item.timestamp {
                                Text(ts)
                                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.4))
                            }
                        }
                    }
                }
                .padding(10)
                .background(Color.white.opacity(0.03))
                .cornerRadius(4)
                .overlay(
                    RoundedRectangle(cornerRadius: 4)
                        .stroke(Color.white.opacity(0.08), lineWidth: 1)
                )
            }
            
            // Bottom Action Bar
            HStack {
                Button(action: {
                    showingResetConfirm = true
                    AudioHapticsService.shared.playKeyClick()
                }) {
                    Text("[RESET QUOTA TODAY]")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(.white.opacity(0.6))
                        .padding(.vertical, 6)
                        .padding(.horizontal, 10)
                        .background(Color.white.opacity(0.05))
                        .cornerRadius(3)
                        .overlay(
                            RoundedRectangle(cornerRadius: 3)
                                .stroke(Color.white.opacity(0.15), lineWidth: 1)
                        )
                }
                .confirmationDialog("Reset Today's Quota?", isPresented: $showingResetConfirm) {
                    Button("Reset Quotas to Zero", role: .destructive) {
                        Task {
                            await client.resetQuota()
                            AudioHapticsService.shared.playTibetanBowl(duration: 2.0)
                        }
                    }
                    Button("Cancel", role: .cancel) {}
                }
                
                Spacer()
                
                // Quick test log button (for testing limits on iOS standalone)
                Menu {
                    Button("+ Log 1 Episode") {
                        client.recordLocalEntertainmentConsumed(type: "series", title: "Test Episode")
                        AudioHapticsService.shared.playKeyClick()
                    }
                    Button("+ Log 1 Movie") {
                        client.recordLocalEntertainmentConsumed(type: "movie", title: "Test Feature Film")
                        AudioHapticsService.shared.playKeyClick()
                    }
                } label: {
                    Text("[+ LOG WATCH]")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                        .padding(.vertical, 6)
                        .padding(.horizontal, 10)
                        .background(Color(red: 0.06, green: 0.78, blue: 0.55).opacity(0.1))
                        .cornerRadius(3)
                        .overlay(
                            RoundedRectangle(cornerRadius: 3)
                                .stroke(Color(red: 0.06, green: 0.78, blue: 0.55).opacity(0.3), lineWidth: 1)
                        )
                }
            }
        }
        .padding(14)
        .background(Color(red: 0.04, green: 0.04, blue: 0.06))
        .cornerRadius(6)
        .overlay(
            RoundedRectangle(cornerRadius: 6)
                .stroke(Color.white.opacity(0.12), lineWidth: 1)
        )
    }
    
    @ViewBuilder
    private func quotaMeterRow(
        title: String,
        badge: String,
        used: Int,
        max: Int,
        remaining: Int,
        unit: String
    ) -> some View {
        let isExhausted = remaining <= 0
        
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(title)
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(.white.opacity(0.9))
                
                Spacer()
                
                Text(badge)
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundColor(isExhausted ? Color.red.opacity(0.8) : Color.white.opacity(0.4))
            }
            
            HStack(spacing: 8) {
                // ASCII capsule meter: [ █ █ ] or [ █ ░ ]
                Text(generateAsciiCapsule(used: used, max: max))
                    .font(.system(size: 13, weight: .bold, design: .monospaced))
                    .foregroundColor(isExhausted ? Color(red: 0.95, green: 0.25, blue: 0.25) : Color(red: 0.06, green: 0.78, blue: 0.55))
                
                Spacer()
                
                Text("\(used)/\(max) \(unit) USED (\(remaining) LEFT)")
                    .font(.system(size: 10, weight: .medium, design: .monospaced))
                    .foregroundColor(isExhausted ? Color.red.opacity(0.9) : .white.opacity(0.6))
            }
        }
        .padding(10)
        .background(Color.white.opacity(0.02))
        .cornerRadius(4)
        .overlay(
            RoundedRectangle(cornerRadius: 4)
                .stroke(Color.white.opacity(0.06), lineWidth: 1)
        )
    }
    
    private func generateAsciiCapsule(used: Int, max: Int) -> String {
        let clampedMax = Swift.max(1, max)
        var str = "[ "
        for i in 0..<clampedMax {
            if i < used {
                str += "█ "
            } else {
                str += "░ "
            }
        }
        str += "]"
        return str
    }
}
