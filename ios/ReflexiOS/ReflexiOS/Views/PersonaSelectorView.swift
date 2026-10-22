import SwiftUI

public struct PersonaSelectorView: View {
    @ObservedObject var client: ReflexClient
    
    public init(client: ReflexClient) {
        self.client = client
    }
    
    public var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                Text("[FOCUS PERSONA // MATRIX]")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                
                Spacer()
                
                Text(client.activeProfile.badge)
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
            }
            
            // Horizontal scroll of Monospace Pill Badges
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(client.allProfiles) { profile in
                        let isSelected = client.activeProfile.id == profile.id
                        Button(action: {
                            Task {
                                await client.switchProfile(to: profile)
                                AudioHapticsService.shared.playSelection()
                                AudioHapticsService.shared.playKeyClick()
                            }
                        }) {
                            Text(profile.badge)
                                .font(.system(size: 11, weight: .bold, design: .monospaced))
                                .foregroundColor(isSelected ? .black : .white.opacity(0.8))
                                .padding(.vertical, 7)
                                .padding(.horizontal, 12)
                                .background(isSelected ? Color(red: 0.06, green: 0.78, blue: 0.55) : Color.white.opacity(0.05))
                                .cornerRadius(4)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 4)
                                        .stroke(isSelected ? Color(red: 0.06, green: 0.78, blue: 0.55) : Color.white.opacity(0.12), lineWidth: 1)
                                )
                        }
                    }
                }
            }
            
            // Persona Details Box
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text(client.activeProfile.name.uppercased())
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                    Spacer()
                }
                
                Text(client.activeProfile.tagline)
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                
                Text(client.activeProfile.description)
                    .font(.system(size: 10, weight: .regular, design: .monospaced))
                    .foregroundColor(.white.opacity(0.65))
                    .lineLimit(2)
            }
            .padding(10)
            .background(Color.white.opacity(0.02))
            .cornerRadius(4)
            .overlay(
                RoundedRectangle(cornerRadius: 4)
                    .stroke(Color.white.opacity(0.06), lineWidth: 1)
            )
            
            // Portals Grid
            VStack(alignment: .leading, spacing: 6) {
                Text("QUICK FOCUS PORTALS:")
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .foregroundColor(.white.opacity(0.45))
                
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 6) {
                    ForEach(client.activeProfile.portals) { portal in
                        if let url = URL(string: portal.url) {
                            Link(destination: url) {
                                HStack(spacing: 6) {
                                    Text("[\(portal.key)]")
                                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                                        .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                                    Text(portal.name)
                                        .font(.system(size: 9, weight: .medium, design: .monospaced))
                                        .foregroundColor(.white.opacity(0.85))
                                        .lineLimit(1)
                                    Spacer()
                                    Image(systemName: "arrow.up.right")
                                        .font(.system(size: 8))
                                        .foregroundColor(.white.opacity(0.3))
                                }
                                .padding(.vertical, 6)
                                .padding(.horizontal, 8)
                                .background(Color.white.opacity(0.04))
                                .cornerRadius(3)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 3)
                                        .stroke(Color.white.opacity(0.08), lineWidth: 1)
                                )
                            }
                        }
                    }
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
}
