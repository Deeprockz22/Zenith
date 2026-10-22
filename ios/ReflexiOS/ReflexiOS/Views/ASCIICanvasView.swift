import SwiftUI

public struct ASCIICanvasView: View {
    @State private var touchLocation: CGPoint? = nil
    @State private var intensity: Double = 1.0
    
    // ASCII ramp from dark to light
    private let ramp: [Character] = Array(" .:-=+*#%@")
    
    public init() {}
    
    public var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            // Header bar in ASCII Magic style
            HStack {
                Text("[ASCII CANVAS // HARMONIC_WAVE]")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55)) // #10b981 emerald
                
                Spacer()
                
                Text("60 FPS // TOUCH_REACTIVE")
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.4))
            }
            .padding(.horizontal, 8)
            
            // Dynamic Interactive ASCII Grid
            TimelineView(.animation) { timeline in
                let time = timeline.date.timeIntervalSinceReferenceDate
                
                GeometryReader { geo in
                    let cols = max(18, Int(geo.size.width / 13))
                    let rows = max(8, Int(geo.size.height / 15))
                    
                    let asciiString = generateASCIIField(
                        cols: cols,
                        rows: rows,
                        time: time,
                        touch: touchLocation,
                        size: geo.size
                    )
                    
                    ZStack {
                        // Pitch black canvas box with monospace border
                        RoundedRectangle(cornerRadius: 4)
                            .fill(Color(red: 0.02, green: 0.02, blue: 0.03))
                            .overlay(
                                RoundedRectangle(cornerRadius: 4)
                                    .stroke(Color.white.opacity(0.12), lineWidth: 1)
                            )
                        
                        Text(asciiString)
                            .font(.system(size: 11, weight: .regular, design: .monospaced))
                            .lineSpacing(-3)
                            .foregroundColor(Color(red: 0.2, green: 0.9, blue: 0.65))
                            .multilineTextAlignment(.leading)
                            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
                            .padding(8)
                    }
                    .gesture(
                        DragGesture(minimumDistance: 0)
                            .onChanged { value in
                                touchLocation = value.location
                                AudioHapticsService.shared.playKeyClick()
                            }
                            .onEnded { _ in
                                touchLocation = nil
                            }
                    )
                }
            }
            .frame(height: 155)
            
            // Sub-status rail
            HStack {
                Text("TOUCH TO PERTURB WAVE")
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.35))
                Spacer()
                Text("RESONANCE: 432Hz")
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(red: 0.06, green: 0.78, blue: 0.55).opacity(0.8))
            }
            .padding(.horizontal, 8)
        }
    }
    
    private func generateASCIIField(
        cols: Int,
        rows: Int,
        time: Double,
        touch: CGPoint?,
        size: CGSize
    ) -> String {
        var result = ""
        result.reserveCapacity(cols * rows + rows)
        
        let normalizedTouchX = touch != nil && size.width > 0 ? (touch!.x / size.width) : 0.5
        let normalizedTouchY = touch != nil && size.height > 0 ? (touch!.y / size.height) : 0.5
        let hasTouch = touch != nil
        
        for r in 0..<rows {
            let ny = Double(r) / Double(rows)
            for c in 0..<cols {
                let nx = Double(c) / Double(cols)
                
                // Base harmonic standing wave
                var v = sin(nx * 5.0 + time * 1.8) * cos(ny * 4.0 - time * 1.2)
                v += 0.5 * sin((nx + ny) * 6.0 + time * 2.2)
                
                // Touch ripple distortion
                if hasTouch {
                    let dx = nx - normalizedTouchX
                    let dy = ny - normalizedTouchY
                    let dist = sqrt(dx * dx + dy * dy)
                    v += 1.8 * sin(dist * 24.0 - time * 6.0) * exp(-dist * 4.0)
                }
                
                // Map [-1.5, 1.5] -> [0, 1]
                let normalized = max(0.0, min(1.0, (v + 1.5) / 3.0))
                let rampIndex = Int(normalized * Double(ramp.count - 1))
                result.append(ramp[rampIndex])
            }
            if r < rows - 1 {
                result.append("\n")
            }
        }
        
        return result
    }
}

#Preview {
    ZStack {
        Color.black.ignoresSafeArea()
        ASCIICanvasView()
            .padding()
    }
}
