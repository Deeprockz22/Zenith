#!/usr/bin/env python3
"""
FocusRedirect: Modular Persona & Profile Engine
Defines specialized intent profiles for different kinds of users:
Software Engineers, Academics & Researchers, Founders & Operators,
Creators & Writers, Balanced Knowledge Workers, and Strict Zen Monk Mode.
"""

PROFILES = {
    "developer": {
        "id": "developer",
        "name": "Software Engineer",
        "badge": "[DEV]",
        "tagline": "CODE // REPOS // RFCs // ARCHITECTURE",
        "description": "Tailored for software engineers, DevOps, and systems programmers.",
        "productive_domains": {
            "github.com", "gitlab.com", "stackoverflow.com", "linear.app",
            "developer.apple.com", "docs.python.org", "rust-lang.org", "pkg.go.dev",
            "news.ycombinator.com", "devdocs.io", "chatgpt.com", "claude.ai",
            "cursor.com", "docker.com", "kubernetes.io", "huggingface.co",
            "leetcode.com", "jira.atlassian.com"
        },
        "allowed_keywords": [
            "coding", "tutorial", "architecture", "debugging", "system design", "golang",
            "rust", "python", "typescript", "react", "docker", "kubernetes", "linux", "kernel",
            "compiler", "database", "sql", "nosql", "algorithm", "leetcode", "benchmark",
            "keynote", "talks at google", "strange loop", "cppcon", "wwdc", "deep dive",
            "computerphile", "numberphile", "devops", "cloud", "aws", "gcp"
        ],
        "allowed_types": ["podcast", "lecture"],
        "portals": [
            {"key": "1", "name": "GITHUB", "url": "https://github.com", "tag": "github.com"},
            {"key": "2", "name": "STACK_OVERFLOW", "url": "https://stackoverflow.com", "tag": "stackoverflow.com"},
            {"key": "3", "name": "DEV_DOCS", "url": "https://devdocs.io", "tag": "devdocs.io"},
            {"key": "4", "name": "LINEAR", "url": "https://linear.app", "tag": "linear.app"},
            {"key": "5", "name": "CLAUDE", "url": "https://claude.ai", "tag": "claude.ai"},
            {"key": "6", "name": "CHATGPT", "url": "https://chatgpt.com", "tag": "chatgpt.com"}
        ]
    },

    "academic": {
        "id": "academic",
        "name": "Student & Scholar",
        "badge": "[STUDENT]",
        "tagline": "COURSES // STUDY // RESEARCH // ASSIGNMENTS",
        "description": "Tailored for students, university scholars, and academic researchers worldwide.",
        "productive_domains": {
            "canvas.instructure.com", "instructure.com", "canvaslms.com", "sso.canvaslms.com",
            "classroom.google.com", "blackboard.com", "moodle.org", "moodle.com",
            "quizlet.com", "coursera.org", "edx.org", "khanacademy.org",
            "overleaf.com", "arxiv.org", "scholar.google.com", "nature.com", "science.org",
            "sciencedirect.com", "jstor.org", "researchgate.net", "semanticscholar.org",
            "notion.so", "chatgpt.com", "claude.ai", "docs.google.com", "github.com"
        },
        "allowed_keywords": [
            "lecture", "mit", "stanford", "cs50", "lecture notes", "symposium", "dissertation",
            "physics", "mathematics", "biology", "mechanics", "cfd", "neural network", "paper review",
            "deep dive", "documentary", "huberman lab", "lex fridman", "mindscape", "veritasium",
            "3blue1brown", "computerphile", "numberphile", "audiobook", "thesis", "coursework",
            "study", "homework", "exam", "syllabus", "tutorial", "academic", "university", "assignment"
        ],
        "allowed_types": ["podcast", "lecture"],
        "portals": [
            {"key": "1", "name": "CANVAS LMS", "url": "https://canvas.instructure.com", "tag": "instructure.com"},
            {"key": "2", "name": "GOOGLE SCHOLAR", "url": "https://scholar.google.com", "tag": "scholar.google.com"},
            {"key": "3", "name": "OVERLEAF", "url": "https://overleaf.com", "tag": "overleaf.com"},
            {"key": "4", "name": "ARXIV", "url": "https://arxiv.org", "tag": "arxiv.org"},
            {"key": "5", "name": "NOTION", "url": "https://notion.so", "tag": "notion.so"},
            {"key": "6", "name": "CLAUDE", "url": "https://claude.ai", "tag": "claude.ai"}
        ]
    },

    "founder": {
        "id": "founder",
        "name": "Founder & Operator",
        "badge": "[EXEC]",
        "tagline": "STRATEGY // REVENUE // PRODUCT // TEAMS",
        "description": "Tailored for startup founders, operators, product managers, and executives.",
        "productive_domains": {
            "linear.app", "stripe.com", "notion.so", "docs.google.com", "mail.google.com",
            "slack.com", "pitchbook.com", "crunchbase.com", "techcrunch.com", "news.ycombinator.com",
            "chatgpt.com", "claude.ai", "linkedin.com", "calendar.google.com"
        },
        "allowed_keywords": [
            "startup", "pitch", "investor", "economics", "strategy", "product management",
            "case study", "acquired", "all-in podcast", "how i built this", "y combinator",
            "market analysis", "saas", "earnings call", "interview", "fireside chat", "macro",
            "venture capital", "leadership", "growth", "metrics", "hiring"
        ],
        "allowed_types": ["podcast", "lecture"],
        "portals": [
            {"key": "1", "name": "LINEAR", "url": "https://linear.app", "tag": "linear.app"},
            {"key": "2", "name": "NOTION", "url": "https://notion.so", "tag": "notion.so"},
            {"key": "3", "name": "STRIPE", "url": "https://dashboard.stripe.com", "tag": "stripe.com"},
            {"key": "4", "name": "GOOGLE_DOCS", "url": "https://docs.google.com", "tag": "docs.google.com"},
            {"key": "5", "name": "GMAIL", "url": "https://mail.google.com", "tag": "mail.google.com"},
            {"key": "6", "name": "CLAUDE", "url": "https://claude.ai", "tag": "claude.ai"}
        ]
    },

    "creator": {
        "id": "creator",
        "name": "Creator & Writer",
        "badge": "[STUDIO]",
        "tagline": "DESIGN // WRITING // ESSAYS // CANVAS",
        "description": "Tailored for UX designers, writers, journalists, and visual creators.",
        "productive_domains": {
            "figma.com", "dribbble.com", "substack.com", "medium.com", "notion.so",
            "canva.com", "webflow.com", "behance.net", "chatgpt.com", "claude.ai",
            "unsplash.com", "docs.google.com"
        },
        "allowed_keywords": [
            "design", "typography", "ui/ux", "screenplay", "creative writing", "critique",
            "essay", "video essay", "film analysis", "documentary", "storytelling", "craft",
            "masterclass", "interview", "podcast", "tim ferriss", "radiolab", "the daily",
            "illustration", "color theory", "animation", "audiobook"
        ],
        "allowed_types": ["podcast", "lecture"],
        "portals": [
            {"key": "1", "name": "FIGMA", "url": "https://figma.com", "tag": "figma.com"},
            {"key": "2", "name": "SUBSTACK", "url": "https://substack.com", "tag": "substack.com"},
            {"key": "3", "name": "NOTION", "url": "https://notion.so", "tag": "notion.so"},
            {"key": "4", "name": "DRIBBBLE", "url": "https://dribbble.com", "tag": "dribbble.com"},
            {"key": "5", "name": "MEDIUM", "url": "https://medium.com", "tag": "medium.com"},
            {"key": "6", "name": "CHATGPT", "url": "https://chatgpt.com", "tag": "chatgpt.com"}
        ]
    },

    "general": {
        "id": "general",
        "name": "Balanced Focus",
        "badge": "[GENERAL]",
        "tagline": "KNOWLEDGE // FOCUS // AUDIO // PORTALS",
        "description": "Universal balanced mode for all-round knowledge work and productivity.",
        "productive_domains": {
            "notion.so", "docs.google.com", "mail.google.com", "chatgpt.com", "claude.ai",
            "github.com", "slack.com", "todoist.com", "calendar.google.com", "linear.app",
            "overleaf.com", "stackoverflow.com"
        },
        "allowed_keywords": [
            "tutorial", "how to", "lecture", "explanation", "analysis", "deep dive",
            "podcast", "interview", "audiobook", "documentary", "keynote", "huberman",
            "lex fridman", "ted talk", "talks at google", "study", "research", "learning"
        ],
        "allowed_types": ["podcast", "lecture"],
        "portals": [
            {"key": "1", "name": "NOTION", "url": "https://notion.so", "tag": "notion.so"},
            {"key": "2", "name": "DOCS", "url": "https://docs.google.com", "tag": "docs.google.com"},
            {"key": "3", "name": "GMAIL", "url": "https://mail.google.com", "tag": "mail.google.com"},
            {"key": "4", "name": "CALENDAR", "url": "https://calendar.google.com", "tag": "calendar.google.com"},
            {"key": "5", "name": "CLAUDE", "url": "https://claude.ai", "tag": "claude.ai"},
            {"key": "6", "name": "CHATGPT", "url": "https://chatgpt.com", "tag": "chatgpt.com"}
        ]
    },

    "zen": {
        "id": "zen",
        "name": "Zen Monk Mode",
        "badge": "[MONK]",
        "tagline": "STRICT // ZERO_MEDIA // NO_NOISE",
        "description": "Strict deep-work mode. Zero video algorithms or casual entertainment.",
        "productive_domains": {
            "github.com", "notion.so", "docs.google.com", "linear.app", "overleaf.com", "figma.com"
        },
        "allowed_keywords": [
            "documentation", "specification", "rfc", "reference manual"
        ],
        "allowed_types": ["lecture"],  # Zen mode strictly blocks casual podcasts on video sites
        "portals": [
            {"key": "1", "name": "WORKSPACE", "url": "https://notion.so", "tag": "notion.so"},
            {"key": "2", "name": "GITHUB", "url": "https://github.com", "tag": "github.com"},
            {"key": "3", "name": "LINEAR", "url": "https://linear.app", "tag": "linear.app"},
            {"key": "4", "name": "DOCS", "url": "https://docs.google.com", "tag": "docs.google.com"},
            {"key": "5", "name": "CLAUDE", "url": "https://claude.ai", "tag": "claude.ai"},
            {"key": "6", "name": "CHATGPT", "url": "https://chatgpt.com", "tag": "chatgpt.com"}
        ]
    }
}

DEFAULT_PROFILE_ID = "general"

def get_profile(profile_id=None):
    """Returns profile dictionary by ID, falling back to general."""
    if profile_id == "student":
        profile_id = "academic"
    if not profile_id or profile_id not in PROFILES:
        return PROFILES[DEFAULT_PROFILE_ID]
    return PROFILES[profile_id]

def serialize_profile(p):
    """Returns a JSON-serializable dictionary representation of a profile."""
    if not p:
        return {}
    d = dict(p)
    if isinstance(d.get("productive_domains"), (set, frozenset)):
        d["productive_domains"] = sorted(list(d["productive_domains"]))
    return d

def list_profiles():
    """Returns a simplified list of profiles for API and CLI."""
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "badge": p["badge"],
            "tagline": p["tagline"],
            "description": p["description"],
            "portals": p["portals"]
        }
        for p in PROFILES.values()
    ]
