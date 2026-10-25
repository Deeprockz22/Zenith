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
        "name": "Aerospace & CFD Engineer",
        "badge": "[AERO_ENG]",
        "tagline": "CFD // AERODYNAMICS // NAVIER_STOKES // MESHING // OPENFOAM",
        "description": "Tailored for Aerospace engineers, aerodynamicists, and CFD numerical simulation practitioners.",
        "productive_domains": {
            "cfd-online.com", "openfoam.com", "openfoam.org", "github.com",
            "su2code.github.io", "paraview.org", "ansys.com", "simscale.com",
            "siemens.com", "scipy.org", "numpy.org", "pytorch.org",
            "overleaf.com", "arxiv.org", "claude.ai", "chatgpt.com", "notion.so"
        },
        "allowed_keywords": [
            "aerodynamics", "cfd", "navier-stokes", "compressible flow", "incompressible",
            "boundary layer", "transonic", "supersonic", "hypersonic", "airfoil", "naca",
            "turbulence", "rans", "les", "dns", "k-omega", "k-epsilon", "reynolds number",
            "mach number", "vortex shedding", "lift", "drag", "shock wave", "finite volume",
            "fvm", "openfoam", "snappyhexminesh", "gmsh", "paraview", "fluent", "star-ccm",
            "su2", "propulsion", "gas turbine", "nozzle", "combustion", "rocketry",
            "computational fluid dynamics", "mesh generation", "aerospace engineering",
            "flight mechanics", "aeroacoustics", "fluid dynamics"
        ],
        "allowed_types": ["podcast", "lecture"],
        "portals": [
            {"key": "1", "name": "CFD_ONLINE", "url": "https://www.cfd-online.com", "tag": "cfd-online.com"},
            {"key": "2", "name": "OPENFOAM", "url": "https://www.openfoam.com", "tag": "openfoam.com"},
            {"key": "3", "name": "SU2_CFD", "url": "https://su2code.github.io", "tag": "su2code.github.io"},
            {"key": "4", "name": "PARAVIEW", "url": "https://www.paraview.org", "tag": "paraview.org"},
            {"key": "5", "name": "ARXIV_FLUIDS", "url": "https://arxiv.org/list/physics.flu-dyn/recent", "tag": "arxiv.org"},
            {"key": "6", "name": "CLAUDE", "url": "https://claude.ai", "tag": "claude.ai"}
        ]
    },

    "academic": {
        "id": "academic",
        "name": "Aerospace Scholar & SciML",
        "badge": "[AERO_GRAD]",
        "tagline": "FLUID_MECHANICS // SciML // PINNs // THESIS // AIAA_JFM",
        "description": "Tailored for Aerospace graduate scholars researching fluid dynamics, PINNs, and Scientific Machine Learning.",
        "productive_domains": {
            "arxiv.org", "scholar.google.com", "sciencedirect.com", "arc.aiaa.org",
            "cambridge.org", "aip.scitation.org", "overleaf.com", "researchgate.net",
            "semanticscholar.org", "deepxde.readthedocs.io", "github.com",
            "notion.so", "chatgpt.com", "claude.ai", "docs.google.com", "nature.com"
        },
        "allowed_keywords": [
            "physics-informed neural networks", "pinn", "scientific machine learning", "sciml",
            "deepxde", "fourier neural operator", "fno", "deeponet", "operator learning",
            "svd", "proper orthogonal decomposition", "pod", "dynamic mode decomposition", "dmd",
            "reduced order model", "rom", "sindy", "brunton", "kutz", "karniadakis",
            "navier-stokes", "fluid mechanics", "journal of fluid mechanics", "jfm", "aiaa",
            "physics of fluids", "thesis", "aerospace", "boundary layer stability",
            "turbulence modeling", "surrogate model", "aerodynamic optimization",
            "direct numerical simulation", "scientific computing", "numerical methods",
            "mit", "stanford", "lecture", "symposium", "paper review", "overleaf", "latex"
        ],
        "allowed_types": ["podcast", "lecture"],
        "portals": [
            {"key": "1", "name": "ARXIV_AERO", "url": "https://arxiv.org/list/physics.flu-dyn/recent", "tag": "arxiv.org"},
            {"key": "2", "name": "GOOGLE SCHOLAR", "url": "https://scholar.google.com", "tag": "scholar.google.com"},
            {"key": "3", "name": "OVERLEAF_THESIS", "url": "https://overleaf.com", "tag": "overleaf.com"},
            {"key": "4", "name": "AIAA_ARC", "url": "https://arc.aiaa.org", "tag": "arc.aiaa.org"},
            {"key": "5", "name": "DEEPXDE_DOCS", "url": "https://deepxde.readthedocs.io", "tag": "deepxde.readthedocs.io"},
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

DEFAULT_PROFILE_ID = "academic"

def get_profile(profile_id=None):
    """Returns profile dictionary by ID, falling back to academic (Aerospace Scholar & SciML)."""
    if profile_id in ("student", "aero_grad", "sciml", "scholar"):
        profile_id = "academic"
    elif profile_id in ("developer", "aero", "cfd", "aero_eng", "engineer"):
        profile_id = "developer"
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
