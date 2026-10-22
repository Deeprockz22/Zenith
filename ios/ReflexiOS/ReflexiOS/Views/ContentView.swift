import SwiftUI

public struct ContentView: View {
    @StateObject private var client = ReflexClient()
    @State private var showingSettings = false
    @State private var selectedTab: Int = 0 // 0: ALL, 1: CANVAS, 2: SPRINT, 3: QUOTA, 4: PERSONAS
    
    public init() {}
    
    public var body: some View {
        ZStack {
            // Pitch black void background
            Color(red: 0.015, green: 0.015, blue: 0.025).ignoresSafeArea()
            
            // Side Rails (Subtle ASCII Magic architectural borders)
            HStack {
                // Left architectural rail
                VStack(spacing: 24) {
                    Text("+")
                    Text("01")
                    Text("ZN")
                    Text("432")
                    Spacer()
                    Text("SYS")
                    Text("OK")
                    Text("+")
                }
                .font(.system(size: 8, weight: .bold, design: .monospaced))
                .foregroundColor(.white.opacity(0.18))
                .frame(width: 14)
                .padding(.vertical, 40)
                
                Spacer()
                
                // Right architectural rail
                VStack(spacing: 24) {
                    Text("+")
                    Text("60")
                    Text("FPS")
                    Text("SEC")
                    Spacer()
                    Text("MONO")
                    Text("NET")
                    Text("+")
                }
                .font(.system(size: 8, weight: .bold, design: .monospaced))
                .foregroundColor(.white.opacity(0.18))
                .frame(width: 14)
                .padding(.vertical, 40)
            }
            .ignoresSafeArea()
            
            // Main content
            VStack(spacing: 0) {
                // Top Navigation Header
                topNavigationBar
                    .padding(.horizontal, 16)
                    .padding(.top, 10)
                    .padding(.bottom, 8)
                
                // Quick Navigation Filter Tabs
                filterTabBar
                    .padding(.horizontal, 16)
                    .padding(.bottom, 8)
                
                Divider()
                    .background(Color.white.opacity(0.1))
                
                // Scrollable Feed
                ScrollView(showsIndicators: false) {
                    VStack(alignment: .leading, spacing: 16) {
                        
                        // Hero ASCII Banner
                        if selectedTab == 0 {
                            heroBanner
                        }
                        
                        // Interactive 60fps ASCII Canvas
                        if selectedTab == 0 || selectedTab == 1 {
                            ASCIICanvasView()
                        }
                        
                        // 25m Focus Sprint Timer & 432Hz Sound
                        if selectedTab == 0 || selectedTab == 2 {
                            StopwatchView()
                        }
                        
                        // Entertainment Quota Capsules
                        if selectedTab == 0 || selectedTab == 3 {
                            QuotaCardView(client: client)
                        }
                        
                        // Persona Matrix & Portals
                        if selectedTab == 0 || selectedTab == 4 {
                            PersonaSelectorView(client: client)
                        }
                        
                        // System Diagnostics Strip
                        systemDiagnosticsStrip
                        
                        // Footer
                        Text("[ZENITH PROTOCOL // AUTONOMOUS FOCUS STUDIO // BUILD 2.4]")
                            .font(.system(size: 8, weight: .bold, design: .monospaced))
                            .foregroundColor(.white.opacity(0.25))
                            .frame(maxWidth: .infinity, alignment: .center)
                            .padding(.top, 10)
                            .padding(.bottom, 30)
                    }
                    .padding(.horizontal, 18)
                    .padding(.top, 14)
                }
            }
        }
        .sheet(isPresented: $showingSettings) {
            SettingsSheetView(client: client)
        }
        .preferredColorScheme(.dark)
    }
    
    // MARK: - Components
    
    private var topNavigationBar: some View {
        HStack {
            HStack(spacing: 6) {
                Circle()
                    .fill(client.state == .connected ? Color(red: 0.06, green: 0.78, blue: 0.55) : Color(red: 0.95, green: 0.65, blue: 0.2))
                    .frame(width: 7, height: 7)
                
                Text("ZENITH // iOS")
                    .font(.system(size: 13, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
            }
            
            Spacer()
            
            // Connection Pill
            Text(client.state.statusIndicator)
                .font(.system(size: 9, weight: .bold, design: .monospaced))
                .foregroundColor(client.state == .connected ? Color(red: 0.06, green: 0.78, blue: 0.55) : Color.white.opacity(0.5))
                .padding(.vertical, 4)
                .padding(.horizontal, 8)
                .background(Color.white.opacity(0.04))
                .cornerRadius(3)
                .overlay(
                    RoundedRectangle(cornerRadius: 3)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
            
            // Config Button
            Button(action: {
                showingSettings = true
                AudioHapticsService.shared.playKeyClick()
            }) {
                Text("[CFG]")
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                    .padding(.vertical, 4)
                    .padding(.horizontal, 8)
                    .background(Color(red: 0.06, green: 0.78, blue: 0.55).opacity(0.12))
                    .cornerRadius(3)
                    .overlay(
                        RoundedRectangle(cornerRadius: 3)
                            .stroke(Color(red: 0.06, green: 0.78, blue: 0.55).opacity(0.3), lineWidth: 1)
                    )
            }
        }
    }
    
    private var filterTabBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 6) {
                tabButton(title: "[ALL]", index: 0)
                tabButton(title: "[WAVE]", index: 1)
                tabButton(title: "[SPRINT]", index: 2)
                tabButton(title: "[QUOTA]", index: 3)
                tabButton(title: "[PERSONA]", index: 4)
            }
        }
    }
    
    @ViewBuilder
    private func tabButton(title: String, index: Int) -> some View {
        let isSelected = selectedTab == index
        Button(action: {
            selectedTab = index
            AudioHapticsService.shared.playSelection()
            AudioHapticsService.shared.playKeyClick()
        }) {
            Text(title)
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundColor(isSelected ? .black : .white.opacity(0.7))
                .padding(.vertical, 5)
                .padding(.horizontal, 9)
                .background(isSelected ? Color(red: 0.06, green: 0.78, blue: 0.55) : Color.white.opacity(0.04))
                .cornerRadius(3)
                .overlay(
                    RoundedRectangle(cornerRadius: 3)
                        .stroke(isSelected ? Color(red: 0.06, green: 0.78, blue: 0.55) : Color.white.opacity(0.08), lineWidth: 1)
                )
        }
    }
    
    private var heroBanner: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("ZENITH ATTENTION ENGINE")
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
            
            Text("HARDWARE-ACCELERATED DUAL SHIELD")
                .font(.system(size: 14, weight: .bold, design: .monospaced))
                .foregroundColor(.white)
            
            Text("SYNCHRONIZED WI-FI TELEMETRY WITH MAC DAEMON + STANDALONE DEEP FOCUS PROTOCOL.")
                .font(.system(size: 9, weight: .regular, design: .monospaced))
                .foregroundColor(.white.opacity(0.5))
                .lineSpacing(2)
        }
        .padding(12)
        .background(Color.white.opacity(0.02))
        .cornerRadius(4)
        .overlay(
            RoundedRectangle(cornerRadius: 4)
                .stroke(Color.white.opacity(0.08), lineWidth: 1)
        )
    }
    
    private var systemDiagnosticsStrip: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text("[DIAGNOSTICS & TELEMETRY]")
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .foregroundColor(.white.opacity(0.4))
                Spacer()
                Text("HOST: \(client.serverHost)")
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.4))
            }
            
            HStack(spacing: 12) {
                diagnosticCell(label: "TOTAL INTERCEPTED", value: "\(client.stats.totalIntercepted)")
                diagnosticCell(label: "SERIES USED", value: "\(client.quota.episodesUsed)/\(client.quota.episodesMax)")
                diagnosticCell(label: "MOVIES USED", value: "\(client.quota.moviesUsed)/\(client.quota.moviesMax)")
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
    
    @ViewBuilder
    private func diagnosticCell(label: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.system(size: 8, weight: .medium, design: .monospaced))
                .foregroundColor(.white.opacity(0.35))
            Text(value)
                .font(.system(size: 11, weight: .bold, design: .monospaced))
                .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

#Preview {
    ContentView()
}
