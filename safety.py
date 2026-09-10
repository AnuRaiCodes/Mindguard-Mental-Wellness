"""
safety.py — Safety Layer for MindGuard
Detects high-risk content and ensures safety responses are always provided.
"""
import re
from typing import Tuple


# ─── Keyword lists ────────────────────────────────────────────────────────────

HIGH_RISK_PATTERNS = [
    # Direct suicide / self-harm
    r"\bsuicid\w*\b",
    r"\bkill\s+(my)?self\b",
    r"\bhurt\s+(my)?self\b",
    r"\bend\s+(my\s+)?life\b",
    r"\bwant\s+to\s+die\b",
    r"\bwish\s+(i\s+were|i\s+was)\s+dead\b",
    r"\bdon'?t\s+want\s+to\s+live\b",
    r"\bno\s+reason\s+to\s+live\b",
    r"\bending\s+it\s+all\b",
    r"\btake\s+my\s+(own\s+)?life\b",
    r"\boverdose\b",
    r"\bself.?harm\b",
    r"\bcutting\s+my?self\b",
    r"\bslit\s+(my\s+)?wrists?\b",
    r"\bjump\s+(from|off)\b",
    r"\bhang\s+(my)?self\b",
    # Burden/hopeless
    r"\beveryone\s+(would\s+be\s+)?better\s+off\s+without\s+me\b",
    r"\bburden\s+to\s+everyone\b",
    r"\bcan'?t\s+(go\s+on|continue)\b",
    r"\bno\s+way\s+out\b",
    r"\btrapped\b.{0,40}\b(pain|die|end)\b",
    # Planning
    r"\bhave\s+a\s+(plan|method)\b",
    r"\bgoodbye\s+forever\b",
    r"\blast\s+(message|time|goodbye)\b",
]

MODERATE_RISK_PATTERNS = [
    r"\bhopeless\b",
    r"\bworthless\b",
    r"\bpointless\b",
    r"\bnumb\b",
    r"\bdesperate\b",
    r"\bfeel\s+(like\s+a\s+)?burden\b",
    r"\bcan'?t\s+(cope|handle|take\s+it)\b",
    r"\bwhat'?s\s+the\s+point\b",
    r"\bwish\s+i\s+(could\s+)?disappear\b",
    r"\bwant\s+to\s+escape\b",
    r"\bgive\s+up\b",
    r"\balone\s+forever\b",
    r"\bnobody\s+cares\b",
    r"\bunloved\b",
]

CRISIS_RESOURCES = """
🆘 **Immediate Support — You are not alone:**

• **iCall (TISS):** 9152987821 *(Mon–Sat, 8am–10pm)*
• **Vandrevala Foundation:** 1860-2662-345 *(24/7, FREE)*
• **AASRA:** 9820466627
• **Emergency Services:** 112
• **Fortis Stress Helpline:** 8376804102

*These are trained, caring professionals who want to listen.*
"""


def check_risk_level(text: str) -> Tuple[str, bool]:
    """
    Analyse text for risk indicators.
    Returns (risk_level, crisis_resources_needed)
    risk_level: 'high' | 'moderate' | 'low'
    """
    text_lower = text.lower()

    for pattern in HIGH_RISK_PATTERNS:
        if re.search(pattern, text_lower):
            return "high", True

    moderate_hits = sum(
        1 for p in MODERATE_RISK_PATTERNS if re.search(p, text_lower)
    )
    if moderate_hits >= 2:
        return "moderate", True
    if moderate_hits >= 1:
        return "moderate", False

    return "low", False


def get_safety_prefix(risk_level: str) -> str:
    """Return a safety prefix to prepend to the agent response for high/moderate risk."""
    if risk_level == "high":
        return (
            "I hear you, and what you're sharing matters deeply to me. "
            "I'm genuinely concerned about your safety right now. "
            "Please know you are not alone, and support is available.\n\n"
            + CRISIS_RESOURCES
            + "\n---\n\n"
        )
    if risk_level == "moderate":
        return (
            "I can hear that you're going through something really difficult. "
            "I want you to know that support is available whenever you need it.\n\n"
            + CRISIS_RESOURCES
            + "\n---\n\n"
        )
    return ""


def build_safe_response(agent_response: str, risk_level: str) -> str:
    """Prepend safety content to agent response when risk is detected."""
    prefix = get_safety_prefix(risk_level)
    if prefix:
        return prefix + agent_response
    return agent_response


def sanitize_response(response: str) -> str:
    """
    Remove any accidental harmful content from AI responses.
    Catches edge cases where the model may have generated unsafe content.
    """
    dangerous_phrases = [
        "here's how to",
        "you could use",
        "an effective method",
        "step by step",
    ]
    # Only flag if combined with dangerous topics
    dangerous_topics = ["overdose", "hanging", "cutting", "jump from", "pills"]

    response_lower = response.lower()
    for topic in dangerous_topics:
        if topic in response_lower:
            for phrase in dangerous_phrases:
                if phrase in response_lower:
                    # Replace the entire response with a safe redirect
                    return (
                        "I care about your wellbeing and safety. "
                        "I'm not able to provide that information, but I'm here to support you. "
                        "Please reach out to a crisis helpline:\n\n"
                        + CRISIS_RESOURCES
                    )
    return response


SAFE_MESSAGING_FOOTER = (
    "\n\n---\n*MindGuard is a wellness companion, not a substitute for professional "
    "mental health care. If you're in crisis, please contact a helpline or emergency services.*"
)
