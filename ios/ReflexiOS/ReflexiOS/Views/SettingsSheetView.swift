import SwiftUI

public struct SettingsSheetView: View {
    @ObservedObject var client: ReflexClient
    @ObservedObject var screenTime = ScreenTimeManager.shared
    @Environment(\.dismiss) private var dismiss
    
    @State private var hostInput: String = ""
    @State private var portInput: String = "5050"
    @State private var standaloneToggle: Bool = false
    @State private var testResult: String? = nil
    @State private var isTesting: Bool = false
    
    public init(client: ReflexClient) {
        self.client = client
    }
    
    public var body: some View {
        NavigationView {
            ZStack {
                Color(red: 0.02, green: 0.02, blue: 0.03).ignoresSafeArea()
                
                ScrollView {
                    VStack(alignment: .leading, spacing: 18) {
                        // Section 1: Mac Host Connection
                        VStack(alignment: .leading, spacing: 10) {
                            Text("[MAC DAEMON BRIDGE // CONFIG]")
                                .font(.system(size: 11, weight: .bold, design: .monospaced))
                                .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                            
                            Text("Enter the local Wi-Fi IP address of your Mac (found in System Settings > Wi-Fi > Details, or run `ipconfig getifaddr en0` in Terminal).")
                                .font(.system(size: 11, weight: .regular, design: .monospaced))
                                .foregroundColor(.white.opacity(0.6))
                            
                            VStack(spacing: 8) {
                                HStack {
                                    Text("IP HOST:")
                                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                                        .foregroundColor(.white.opacity(0.7))
                                        .frame(width: 80, alignment: .leading)
                                    
                                    TextField("192.168.1.X or localhost", text: $hostInput)
                                        .font(.system(size: 12, weight: .medium, design: .monospaced))
                                        .foregroundColor(.white)
                                        .autocapitalization(.none)
                                        .disableAutocorrection(true)
                                        .padding(8)
                                        .background(Color.white.opacity(0.05))
                                        .cornerRadius(4)
                                }
                                
                                HStack {
                                    Text("PORT:")
                                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                                        .foregroundColor(.white.opacity(0.7))
                                        .frame(width: 80, alignment: .leading)
                                    
                                    TextField("5050", text: $portInput)
                                        .font(.system(size: 12, weight: .medium, design: .monospaced))
                                        .foregroundColor(.white)
                                        .keyboardType(.numberPad)
                                        .padding(8)
                                        .background(Color.white.opacity(0.05))
                                        .cornerRadius(4)
                                }
                            }
                            
                            // Test Ping Button
                            HStack {
                                Button(action: testConnection) {
                                    HStack(spacing: 6) {
                                        if isTesting {
                                            ProgressView()
                                                .progressViewStyle(CircularProgressViewStyle(tint: .black))
                                                .scaleEffect(0.7)
                                        }
                                        Text(isTesting ? "[TESTING...]" : "[TEST CONNECTION]")
                                            .font(.system(size: 10, weight: .bold, design: .monospaced))
                                    }
                                    .foregroundColor(.black)
                                    .padding(.vertical, 7)
                                    .padding(.horizontal, 12)
                                    .background(Color(red: 0.06, green: 0.78, blue: 0.55))
                                    .cornerRadius(3)
                                }
                                
                                Spacer()
                                
                                if let res = testResult {
                                    Text(res)
                                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                                        .foregroundColor(res.contains("OK") ? Color(red: 0.06, green: 0.78, blue: 0.55) : Color.red.opacity(0.9))
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
                        
                        // Section 2: Mode Toggle
                        VStack(alignment: .leading, spacing: 10) {
                            Text("[STANDALONE // OFFLINE MODE]")
                                .font(.system(size: 11, weight: .bold, design: .monospaced))
                                .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                            
                            Toggle(isOn: $standaloneToggle) {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Force Standalone iOS Mode")
                                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                                        .foregroundColor(.white)
                                    Text("Disables Wi-Fi polling and runs full timer, breathing, and quota logs offline on device.")
                                        .font(.system(size: 10, weight: .regular, design: .monospaced))
                                        .foregroundColor(.white.opacity(0.55))
                                }
                            }
                            .tint(Color(red: 0.06, green: 0.78, blue: 0.55))
                        }
                        .padding(14)
                        .background(Color(red: 0.04, green: 0.04, blue: 0.06))
                        .cornerRadius(6)
                        .overlay(
                            RoundedRectangle(cornerRadius: 6)
                                .stroke(Color.white.opacity(0.12), lineWidth: 1)
                        )
                        
                        // Section 3: Screen Time & Shield
                        VStack(alignment: .leading, spacing: 10) {
                            Text("[SCREEN TIME // FAMILY CONTROLS]")
                                .font(.system(size: 11, weight: .bold, design: .monospaced))
                                .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                            
                            Text("Status: \(screenTime.statusMessage)")
                                .font(.system(size: 11, weight: .bold, design: .monospaced))
                                .foregroundColor(.white.opacity(0.8))
                            
                            Button(action: {
                                Task {
                                    await screenTime.requestAuthorization()
                                    AudioHapticsService.shared.playKeyClick()
                                }
                            }) {
                                Text(screenTime.isAuthorized ? "[AUTH VERIFIED // ACTIVE]" : "[AUTHORIZE SCREEN TIME]")
                                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                                    .foregroundColor(screenTime.isAuthorized ? .black : Color(red: 0.06, green: 0.78, blue: 0.55))
                                    .padding(.vertical, 8)
                                    .padding(.horizontal, 12)
                                    .background(screenTime.isAuthorized ? Color(red: 0.06, green: 0.78, blue: 0.55) : Color(red: 0.06, green: 0.78, blue: 0.55).opacity(0.15))
                                    .cornerRadius(3)
                            }
                        }
                        .padding(14)
                        .background(Color(red: 0.04, green: 0.04, blue: 0.06))
                        .cornerRadius(6)
                        .overlay(
                            RoundedRectangle(cornerRadius: 6)
                                .stroke(Color.white.opacity(0.12), lineWidth: 1)
                        )
                        
                        // Section 4: Sideloading Info Box
                        VStack(alignment: .leading, spacing: 8) {
                            Text("[PERSONAL PROVISIONING]")
                                .font(.system(size: 11, weight: .bold, design: .monospaced))
                                .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                            
                            Text("This build is compiled for self-hosted sideloading. No App Store review or subscription required. Use Xcode with a free personal Apple ID to sign and install.")
                                .font(.system(size: 10, weight: .regular, design: .monospaced))
                                .foregroundColor(.white.opacity(0.6))
                        }
                        .padding(14)
                        .background(Color.white.opacity(0.02))
                        .cornerRadius(6)
                        .overlay(
                            RoundedRectangle(cornerRadius: 6)
                                .stroke(Color.white.opacity(0.06), lineWidth: 1)
                        )
                    }
                    .padding(16)
                }
            }
            .navigationTitle("SYSTEM CONFIG")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("[SAVE]") {
                        saveSettings()
                        dismiss()
                    }
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                }
                
                ToolbarItem(placement: .cancellationAction) {
                    Button("[CLOSE]") {
                        dismiss()
                    }
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(.white.opacity(0.6))
                }
            }
        }
        .onAppear {
            hostInput = client.serverHost
            portInput = String(client.serverPort)
            standaloneToggle = client.forceStandalone
        }
    }
    
    private func saveSettings() {
        client.serverHost = hostInput.trimmingCharacters(in: .whitespacesAndNewlines)
        if let p = Int(portInput.trimmingCharacters(in: .whitespacesAndNewlines)), p > 0 {
            client.serverPort = p
        }
        client.forceStandalone = standaloneToggle
        AudioHapticsService.shared.playKeyClick()
        Task {
            await client.pollServer()
        }
    }
    
    private func testConnection() {
        isTesting = true
        testResult = nil
        AudioHapticsService.shared.playKeyClick()
        
        let testHost = hostInput.trimmingCharacters(in: .whitespacesAndNewlines)
        let testPort = Int(portInput) ?? 5050
        guard let url = URL(string: "http://\(testHost):\(testPort)/api/stats") else {
            isTesting = false
            testResult = "INVALID URL"
            return
        }
        
        Task {
            do {
                let config = URLSessionConfiguration.ephemeral
                config.timeoutIntervalForRequest = 2.0
                let session = URLSession(configuration: config)
                let (_, response) = try await session.data(from: url)
                if let http = response as? HTTPURLResponse, http.statusCode == 200 {
                    testResult = "PING OK [200]"
                    AudioHapticsService.shared.playTibetanBowl(duration: 1.5)
                } else {
                    testResult = "HTTP ERROR"
                }
            } catch {
                testResult = "FAIL: NO SIGNAL"
            }
            isTesting = false
        }
    }
}
