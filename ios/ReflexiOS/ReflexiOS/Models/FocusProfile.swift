import Foundation

public struct FocusPortal: Codable, Identifiable, Hashable {
    public var id: String { key }
    public let key: String
    public let name: String
    public let url: String
    public let tag: String
}

public struct FocusProfile: Codable, Identifiable, Hashable {
    public let id: String
    public let name: String
    public let badge: String
    public let tagline: String
    public let description: String
    public let portals: [FocusPortal]
    
    public static let student = FocusProfile(
        id: "academic",
        name: "Student & Scholar",
        badge: "[STUDENT]",
        tagline: "COURSES // STUDY // RESEARCH // ASSIGNMENTS",
        description: "Tailored for students, university scholars, and academic researchers worldwide.",
        portals: [
            FocusPortal(key: "1", name: "CANVAS LMS", url: "https://canvas.instructure.com", tag: "instructure.com"),
            FocusPortal(key: "2", name: "GOOGLE SCHOLAR", url: "https://scholar.google.com", tag: "scholar.google.com"),
            FocusPortal(key: "3", name: "OVERLEAF", url: "https://overleaf.com", tag: "overleaf.com"),
            FocusPortal(key: "4", name: "ARXIV", url: "https://arxiv.org", tag: "arxiv.org"),
            FocusPortal(key: "5", name: "NOTION", url: "https://notion.so", tag: "notion.so"),
            FocusPortal(key: "6", name: "CLAUDE", url: "https://claude.ai", tag: "claude.ai")
        ]
    )
    
    public static let developer = FocusProfile(
        id: "developer",
        name: "Software Engineer",
        badge: "[DEV]",
        tagline: "CODE // REPOS // RFCs // ARCHITECTURE",
        description: "Tailored for software engineers, DevOps, and systems programmers.",
        portals: [
            FocusPortal(key: "1", name: "GITHUB", url: "https://github.com", tag: "github.com"),
            FocusPortal(key: "2", name: "STACK_OVERFLOW", url: "https://stackoverflow.com", tag: "stackoverflow.com"),
            FocusPortal(key: "3", name: "DEV_DOCS", url: "https://devdocs.io", tag: "devdocs.io"),
            FocusPortal(key: "4", name: "LINEAR", url: "https://linear.app", tag: "linear.app"),
            FocusPortal(key: "5", name: "CLAUDE", url: "https://claude.ai", tag: "claude.ai"),
            FocusPortal(key: "6", name: "CHATGPT", url: "https://chatgpt.com", tag: "chatgpt.com")
        ]
    )
    
    public static let founder = FocusProfile(
        id: "founder",
        name: "Founder & Operator",
        badge: "[EXEC]",
        tagline: "STRATEGY // REVENUE // PRODUCT // TEAMS",
        description: "Tailored for startup founders, operators, product managers, and executives.",
        portals: [
            FocusPortal(key: "1", name: "LINEAR", url: "https://linear.app", tag: "linear.app"),
            FocusPortal(key: "2", name: "NOTION", url: "https://notion.so", tag: "notion.so"),
            FocusPortal(key: "3", name: "STRIPE", url: "https://dashboard.stripe.com", tag: "stripe.com"),
            FocusPortal(key: "4", name: "GOOGLE_DOCS", url: "https://docs.google.com", tag: "docs.google.com"),
            FocusPortal(key: "5", name: "GMAIL", url: "https://mail.google.com", tag: "mail.google.com"),
            FocusPortal(key: "6", name: "CLAUDE", url: "https://claude.ai", tag: "claude.ai")
        ]
    )
    
    public static let creator = FocusProfile(
        id: "creator",
        name: "Creator & Writer",
        badge: "[STUDIO]",
        tagline: "DESIGN // WRITING // ESSAYS // CANVAS",
        description: "Tailored for UX designers, writers, journalists, and visual creators.",
        portals: [
            FocusPortal(key: "1", name: "FIGMA", url: "https://figma.com", tag: "figma.com"),
            FocusPortal(key: "2", name: "SUBSTACK", url: "https://substack.com", tag: "substack.com"),
            FocusPortal(key: "3", name: "NOTION", url: "https://notion.so", tag: "notion.so"),
            FocusPortal(key: "4", name: "DRIBBBLE", url: "https://dribbble.com", tag: "dribbble.com"),
            FocusPortal(key: "5", name: "MEDIUM", url: "https://medium.com", tag: "medium.com"),
            FocusPortal(key: "6", name: "CHATGPT", url: "https://chatgpt.com", tag: "chatgpt.com")
        ]
    )
    
    public static let general = FocusProfile(
        id: "general",
        name: "Balanced Focus",
        badge: "[GENERAL]",
        tagline: "KNOWLEDGE // FOCUS // AUDIO // PORTALS",
        description: "Universal balanced mode for all-round knowledge work and productivity.",
        portals: [
            FocusPortal(key: "1", name: "NOTION", url: "https://notion.so", tag: "notion.so"),
            FocusPortal(key: "2", name: "DOCS", url: "https://docs.google.com", tag: "docs.google.com"),
            FocusPortal(key: "3", name: "GMAIL", url: "https://mail.google.com", tag: "mail.google.com"),
            FocusPortal(key: "4", name: "CALENDAR", url: "https://calendar.google.com", tag: "calendar.google.com"),
            FocusPortal(key: "5", name: "CLAUDE", url: "https://claude.ai", tag: "claude.ai"),
            FocusPortal(key: "6", name: "CHATGPT", url: "https://chatgpt.com", tag: "chatgpt.com")
        ]
    )
    
    public static let zen = FocusProfile(
        id: "zen",
        name: "Zen Monk Mode",
        badge: "[MONK]",
        tagline: "STRICT // ZERO_MEDIA // NO_NOISE",
        description: "Strict deep-work mode. Zero video algorithms or casual entertainment.",
        portals: [
            FocusPortal(key: "1", name: "WORKSPACE", url: "https://notion.so", tag: "notion.so"),
            FocusPortal(key: "2", name: "GITHUB", url: "https://github.com", tag: "github.com"),
            FocusPortal(key: "3", name: "LINEAR", url: "https://linear.app", tag: "linear.app"),
            FocusPortal(key: "4", name: "DOCS", url: "https://docs.google.com", tag: "docs.google.com"),
            FocusPortal(key: "5", name: "CLAUDE", url: "https://claude.ai", tag: "claude.ai"),
            FocusPortal(key: "6", name: "CHATGPT", url: "https://chatgpt.com", tag: "chatgpt.com")
        ]
    )
    
    public static let defaultProfiles: [FocusProfile] = [
        .student, .developer, .founder, .creator, .general, .zen
    ]
}
