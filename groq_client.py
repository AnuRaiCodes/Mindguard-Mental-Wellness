"""
groq_client.py — Groq API integration for MindGuard
Handles all LLM calls with retry logic and demo/mock mode.
"""
import os
import logging
import time
import random
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("groq package not installed")


# ─── Demo responses for MOCK mode ────────────────────────────────────────────

DEMO_RESPONSES = {
    "AWARENESS_AGENT": [
        "Mental health is just as important as physical health. Conditions like anxiety and depression are common, treatable, and nothing to be ashamed of. In India, about 150 million people need mental health support, but stigma often prevents people from seeking help. Remember: seeing a counselor is as normal as seeing a doctor for a fever. What aspect of mental health would you like to learn more about?",
        "Stress is your body's natural response to challenges. Short-term stress can be motivating, but chronic stress affects both physical and mental health. Common signs include sleep problems, irritability, difficulty concentrating, and physical tension. The good news is that there are many effective, evidence-based strategies to manage stress. Would you like to explore some of them?",
        "Anxiety is a normal human emotion, but when it becomes persistent and interferes with daily life, it may indicate an anxiety disorder. Symptoms can include excessive worry, restlessness, physical tension, and avoiding certain situations. Anxiety disorders are among the most treatable mental health conditions — with therapy, lifestyle changes, and sometimes medication, most people improve significantly.",
    ],
    "EMOTIONAL_SUPPORT_AGENT": [
        "I hear you, and what you're sharing means a lot. It sounds like you're carrying a lot right now, and that takes real courage to acknowledge. Your feelings are completely valid — whatever you're going through is real and it matters. You don't have to have all the answers or fix everything at once. I'm here with you. Would it help to talk more about what's been weighing on you?",
        "That sounds incredibly difficult, and I want you to know you're not alone in feeling this way. So many people experience moments like this, even if they don't talk about it. Thank you for trusting me with this. It's okay not to be okay. Sometimes just acknowledging how we feel is the first step toward finding our way through. What do you need most right now — someone to listen, or some ideas that might help?",
        "I can hear how exhausted you are, and that makes complete sense given everything you're dealing with. Feeling overwhelmed doesn't mean you're weak — it means you've been strong for too long without enough support. You deserve care and kindness, especially from yourself. How long have you been feeling this way?",
    ],
    "RISK_SCREENING_AGENT": [
        "I hear you, and I'm genuinely concerned about your safety. What you're sharing matters deeply, and you deserve support right now.\n\n🆘 **Please reach out to:**\n• **iCall (TISS):** 9152987821 *(Mon–Sat, 8am–10pm)*\n• **Vandrevala Foundation:** 1860-2662-345 *(24/7, FREE)*\n• **Emergency:** 112\n\nYou don't have to face this alone. Are you safe right now? I'm here with you.",
    ],
    "PREVENTION_SUPPORT_AGENT": [
        "One of the most effective quick techniques for stress is **deep breathing**. Try this:\n\n1. Breathe in slowly through your nose for **4 counts**\n2. Hold for **2 counts**\n3. Exhale slowly through your mouth for **6 counts**\n4. Repeat 5 times\n\nThis activates your parasympathetic nervous system (your calm-down system) within minutes. Would you like to try it now, or would you prefer a different technique?",
        "Finding a therapist in India is more accessible than many people think:\n\n• **iCall (TISS):** 9152987821 | Free/low-cost, specializes in students\n• **The Mind Clan:** themindclan.com — verified therapist directory\n• **YourDOST:** yourdost.com — online counseling\n• **Practo/1mg** — book appointments with psychologists near you\n• **College counseling centers** — often free for students\n\nWould you like more information about what to expect in a first therapy session?",
        "Journaling can be a powerful tool for processing emotions and tracking mood patterns. You don't need to write perfectly — even a few sentences a day helps. Try starting with: 'Today I felt _____ because _____. One thing I can do for myself today is _____.' Would you like to try a guided journal entry right here in MindGuard?",
    ],
    "ORCHESTRATOR": ["EMOTIONAL_SUPPORT_AGENT"],
}


class GroqClient:
    """Groq API client with retry logic, fallback, and demo mode support."""

    def __init__(self, api_key: str, model: str, fast_model: str, demo_mode: bool = False):
        self.api_key = api_key
        self.model = model
        self.fast_model = fast_model
        self.demo_mode = demo_mode or not api_key or not GROQ_AVAILABLE
        self.client = None

        if not self.demo_mode and GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=api_key)
                logger.info("Groq client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.demo_mode = True

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        agent_name: str = "EMOTIONAL_SUPPORT_AGENT",
    ) -> str:
        """Send a chat completion request to Groq."""
        if self.demo_mode:
            return self._demo_response(agent_name)

        target_model = model or self.model
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                error_str = str(e).lower()
                if "rate_limit" in error_str or "429" in error_str:
                    wait = 2 ** attempt + random.uniform(0, 1)
                    logger.warning(f"Rate limited. Waiting {wait:.1f}s… (attempt {attempt+1})")
                    time.sleep(wait)
                elif "model_not_found" in error_str and target_model != self.fast_model:
                    logger.warning(f"Model not found, falling back to {self.fast_model}")
                    target_model = self.fast_model
                else:
                    logger.error(f"Groq API error: {e}")
                    if attempt == 2:
                        return self._demo_response(agent_name)

        return self._demo_response(agent_name)

    def route(self, messages: List[Dict[str, str]]) -> str:
        """Use the fast model for quick routing decisions."""
        if self.demo_mode:
            return random.choice(list(DEMO_RESPONSES["ORCHESTRATOR"]))

        try:
            response = self.client.chat.completions.create(
                model=self.fast_model,
                messages=messages,
                temperature=0.1,
                max_tokens=20,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            logger.error(f"Routing error: {e}")
            return "EMOTIONAL_SUPPORT_AGENT"

    def _demo_response(self, agent_name: str) -> str:
        responses = DEMO_RESPONSES.get(agent_name, DEMO_RESPONSES["EMOTIONAL_SUPPORT_AGENT"])
        return random.choice(responses)

    @property
    def is_demo(self) -> bool:
        return self.demo_mode


# Singleton
_groq_client: GroqClient | None = None


def get_groq_client(app=None) -> GroqClient:
    global _groq_client
    if _groq_client is None:
        if app:
            _groq_client = GroqClient(
                api_key=app.config.get("GROQ_API_KEY", ""),
                model=app.config.get("GROQ_MODEL", "llama3-70b-8192"),
                fast_model=app.config.get("GROQ_FAST_MODEL", "llama3-8b-8192"),
                demo_mode=app.config.get("DEMO_MODE", False),
            )
        else:
            _groq_client = GroqClient(
                api_key=os.environ.get("GROQ_API_KEY", ""),
                model="llama3-70b-8192",
                fast_model="llama3-8b-8192",
                demo_mode=os.environ.get("DEMO_MODE", "false").lower() == "true",
            )
    return _groq_client
