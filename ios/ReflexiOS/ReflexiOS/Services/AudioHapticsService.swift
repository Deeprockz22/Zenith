#if canImport(UIKit)
import UIKit
#endif
import AVFoundation

public final class AudioHapticsService {
    public static let shared = AudioHapticsService()
    
    private var engine: AVAudioEngine?
    private var playerNode: AVAudioPlayerNode?
    private var audioFormat: AVAudioFormat?
    
    // Haptic feedback generators
    #if canImport(UIKit)
    private let lightImpact = UIImpactFeedbackGenerator(style: .light)
    private let mediumImpact = UIImpactFeedbackGenerator(style: .medium)
    private let heavyImpact = UIImpactFeedbackGenerator(style: .heavy)
    private let selectionFeedback = UISelectionFeedbackGenerator()
    private let notificationFeedback = UINotificationFeedbackGenerator()
    #endif
    
    private init() {
        prepareHaptics()
        setupAudioSession()
    }
    
    // MARK: - Haptic Patterns
    public func prepareHaptics() {
        #if canImport(UIKit)
        lightImpact.prepare()
        mediumImpact.prepare()
        heavyImpact.prepare()
        selectionFeedback.prepare()
        notificationFeedback.prepare()
        #endif
    }
    
    public func playKeyClick() {
        #if canImport(UIKit)
        lightImpact.impactOccurred(intensity: 0.7)
        #endif
    }
    
    public func playSelection() {
        #if canImport(UIKit)
        selectionFeedback.selectionChanged()
        #endif
    }
    
    public func playSprintComplete() {
        #if canImport(UIKit)
        heavyImpact.impactOccurred(intensity: 1.0)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) { [weak self] in
            self?.mediumImpact.impactOccurred(intensity: 0.8)
        }
        #endif
    }
    
    public func playWarning() {
        #if canImport(UIKit)
        notificationFeedback.notificationOccurred(.warning)
        #endif
    }
    
    // MARK: - 432Hz Tibetan Singing Bowl Synthesis
    private func setupAudioSession() {
        do {
            try AVAudioSession.sharedInstance().setCategory(.ambient, mode: .default, options: [.mixWithOthers])
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("Audio session configuration error: \(error)")
        }
    }
    
    public func playTibetanBowl(duration: Double = 3.5) {
        Task {
            playSynthesizedBowl(duration: duration)
        }
    }
    
    private func playSynthesizedBowl(duration: Double) {
        let sampleRate: Double = 44100.0
        let frameCount = AVAudioFrameCount(sampleRate * duration)
        
        guard let format = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 1),
              let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: frameCount) else {
            return
        }
        buffer.frameLength = frameCount
        
        guard let floatChannelData = buffer.floatChannelData else { return }
        let channel = floatChannelData[0]
        
        // Frequencies: Fundamental 432Hz, 1st overtone 864Hz, 2nd overtone 1296Hz
        let f0 = 432.0
        let f1 = 864.0
        let f2 = 1296.0
        
        for i in 0..<Int(frameCount) {
            let t = Double(i) / sampleRate
            // Exponential decay envelope
            let envelope = exp(-t * 1.4)
            // Gentle modulation
            let mod = 1.0 + 0.05 * sin(2.0 * .pi * 2.5 * t)
            
            let sample = (
                0.7 * sin(2.0 * .pi * f0 * t) +
                0.2 * sin(2.0 * .pi * f1 * t) +
                0.1 * sin(2.0 * .pi * f2 * t)
            ) * envelope * mod * 0.35
            
            channel[i] = Float(sample)
        }
        
        let localEngine = AVAudioEngine()
        let localPlayer = AVAudioPlayerNode()
        localEngine.attach(localPlayer)
        localEngine.connect(localPlayer, to: localEngine.mainMixerNode, format: format)
        
        do {
            try localEngine.start()
            localPlayer.play()
            localPlayer.scheduleBuffer(buffer, at: nil, options: .interrupts) {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                    localPlayer.stop()
                    localEngine.stop()
                }
            }
        } catch {
            print("Bowl playback failed: \(error)")
        }
    }
}
