import SwiftUI
import Combine

public struct StopwatchView: View {
    @State private var timeRemaining: Int = 25 * 60 // 25 minutes default
    @State private var totalTime: Int = 25 * 60
    @State private var isRunning: Bool = false
    @State private var timerSubscription: AnyCancellable?
    
    public init() {}
    
    public var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                Text("[FOCUS SPRINT ENGINE // 25M]")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                
                Spacer()
                
                Text(isRunning ? "ACTIVE // 432Hz" : "STANDBY")
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .foregroundColor(isRunning ? Color(red: 0.06, green: 0.78, blue: 0.55) : .white.opacity(0.4))
            }
            
            // Giant Monospace Time Display
            VStack(spacing: 6) {
                Text(formatTime(timeRemaining))
                    .font(.system(size: 44, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
                    .tracking(2)
                    .shadow(color: isRunning ? Color(red: 0.06, green: 0.78, blue: 0.55).opacity(0.3) : .clear, radius: 10)
                
                // ASCII Progress Bar
                let progress = totalTime > 0 ? Double(totalTime - timeRemaining) / Double(totalTime) : 0.0
                HStack(spacing: 6) {
                    Text(generateAsciiProgressBar(progress: progress, length: 18))
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                    
                    Text("\(Int(progress * 100))%")
                        .font(.system(size: 10, weight: .medium, design: .monospaced))
                        .foregroundColor(.white.opacity(0.5))
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)
            .background(Color.white.opacity(0.02))
            .cornerRadius(4)
            .overlay(
                RoundedRectangle(cornerRadius: 4)
                    .stroke(Color.white.opacity(0.08), lineWidth: 1)
            )
            
            // Control Buttons
            HStack(spacing: 10) {
                // Play / Pause Button
                Button(action: toggleTimer) {
                    HStack(spacing: 6) {
                        Text(isRunning ? "[PAUSE]" : "[START SPRINT]")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                    }
                    .foregroundColor(.black)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(isRunning ? Color.white : Color(red: 0.06, green: 0.78, blue: 0.55))
                    .cornerRadius(4)
                }
                
                // Reset Button
                Button(action: resetTimer) {
                    Text("[RESET]")
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .foregroundColor(.white.opacity(0.8))
                        .padding(.vertical, 10)
                        .padding(.horizontal, 14)
                        .background(Color.white.opacity(0.06))
                        .cornerRadius(4)
                        .overlay(
                            RoundedRectangle(cornerRadius: 4)
                                .stroke(Color.white.opacity(0.15), lineWidth: 1)
                        )
                }
                
                // 432Hz Sound Chime Button
                Button(action: {
                    AudioHapticsService.shared.playTibetanBowl(duration: 4.0)
                    AudioHapticsService.shared.playKeyClick()
                }) {
                    Text("[432Hz]")
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55))
                        .padding(.vertical, 10)
                        .padding(.horizontal, 12)
                        .background(Color(red: 0.06, green: 0.78, blue: 0.55).opacity(0.1))
                        .cornerRadius(4)
                        .overlay(
                            RoundedRectangle(cornerRadius: 4)
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
    
    private func toggleTimer() {
        AudioHapticsService.shared.playKeyClick()
        if isRunning {
            stopTimer()
        } else {
            startTimer()
            AudioHapticsService.shared.playTibetanBowl(duration: 2.5)
        }
    }
    
    private func startTimer() {
        isRunning = true
        timerSubscription = Timer.publish(every: 1.0, on: .main, in: .common)
            .autoconnect()
            .sink { _ in
                if self.timeRemaining > 0 {
                    self.timeRemaining -= 1
                } else {
                    self.stopTimer()
                    AudioHapticsService.shared.playSprintComplete()
                    AudioHapticsService.shared.playTibetanBowl(duration: 5.0)
                }
            }
    }
    
    private func stopTimer() {
        isRunning = false
        timerSubscription?.cancel()
        timerSubscription = nil
    }
    
    private func resetTimer() {
        AudioHapticsService.shared.playKeyClick()
        stopTimer()
        timeRemaining = totalTime
    }
    
    private func formatTime(_ seconds: Int) -> String {
        let mins = seconds / 60
        let secs = seconds % 60
        return String(format: "%02d:%02d", mins, secs)
    }
    
    private func generateAsciiProgressBar(progress: Double, length: Int) -> String {
        let filledCount = min(length, max(0, Int(progress * Double(length))))
        let emptyCount = length - filledCount
        return "[" + String(repeating: "█", count: filledCount) + String(repeating: "░", count: emptyCount) + "]"
    }
}
