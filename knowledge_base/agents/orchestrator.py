"""
agents/orchestrator.py — Multi-agent Orchestrator for MindGuard

Flow: User Message → Safety Check → Orchestrator → Agent → RAG → Groq API → Safety Check → Response
"""
import logging
from typing import Dict, List, Tuple

from .instructions import (
    GLOBAL_RULES,
    ORCHESTRATOR_INSTRUCTIONS,
    AGENT_INSTRUCTIONS_MAP,
    AGENT_DISPLAY_NAMES,
    AGENT_ICONS,
)
from safety import check_risk_level, build_safe_response, sanitize_response, SAFE_MESSAGING_FOOTER

logger = logging.getLogger(__name__)

VALID_AGENTS = list(AGENT_INSTRUCTIONS_MAP.keys())


class Orchestrator:
    """
    Central orchestrator that routes user messages to the appropriate
    specialized agent, retrieves RAG context, calls Groq, and enforces
    the safety layer.
    """

    def __init__(self, groq_client, rag_pipeline):
        self.groq = groq_client
        self.rag = rag_pipeline

    def process(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]],
        user_context: Dict | None = None,
    ) -> Dict:
        """
        Main entry point.

        Returns:
            {
                "response": str,
                "agent_used": str,
                "risk_level": str,
                "crisis_resources_needed": bool,
                "rag_context_used": bool,
            }
        """
        # ── Step 1: Safety pre-check on user message ────────────────────────
        risk_level, crisis_needed = check_risk_level(user_message)

        # High-risk → always go to Risk Screening Agent
        if risk_level == "high":
            agent_name = "RISK_SCREENING_AGENT"
            logger.warning(f"HIGH RISK detected — routing to RISK_SCREENING_AGENT")
        else:
            # ── Step 2: Routing via Orchestrator ────────────────────────────
            agent_name = self._route(user_message, chat_history)

        # ── Step 3: Retrieve RAG context ────────────────────────────────────
        rag_context = ""
        rag_used = False
        if self.rag:
            try:
                rag_context = self.rag.retrieve(user_message)
                rag_used = bool(rag_context)
            except Exception as e:
                logger.error(f"RAG retrieval failed: {e}")

        # ── Step 4: Build messages for the agent ────────────────────────────
        messages = self._build_messages(
            agent_name=agent_name,
            user_message=user_message,
            chat_history=chat_history,
            rag_context=rag_context,
            user_context=user_context,
            risk_level=risk_level,
        )

        # ── Step 5: Call Groq API ────────────────────────────────────────────
        raw_response = self.groq.chat(messages=messages, agent_name=agent_name)

        # ── Step 6: Safety post-check on response ───────────────────────────
        safe_response = sanitize_response(raw_response)
        final_response = build_safe_response(safe_response, risk_level)

        # Add safe messaging footer for moderate/high risk
        if risk_level in ("high", "moderate"):
            if SAFE_MESSAGING_FOOTER not in final_response:
                final_response += SAFE_MESSAGING_FOOTER

        return {
            "response": final_response,
            "agent_used": agent_name,
            "agent_display_name": AGENT_DISPLAY_NAMES.get(agent_name, agent_name),
            "agent_icon": AGENT_ICONS.get(agent_name, "🤖"),
            "risk_level": risk_level,
            "crisis_resources_needed": crisis_needed,
            "rag_context_used": rag_used,
        }

    def _route(self, user_message: str, chat_history: List[Dict]) -> str:
        """Use the fast LLM to determine which agent should handle the message."""
        routing_messages = [
            {"role": "system", "content": ORCHESTRATOR_INSTRUCTIONS},
            {
                "role": "user",
                "content": (
                    f"Recent context: {self._summarize_history(chat_history)}\n\n"
                    f"New message: {user_message}\n\n"
                    "Which agent should handle this? Reply with ONLY the agent name."
                ),
            },
        ]

        raw = self.groq.route(routing_messages).strip().upper()

        # Validate — find best match
        for agent in VALID_AGENTS:
            if agent in raw:
                return agent

        logger.warning(f"Router returned unknown agent '{raw}', defaulting to EMOTIONAL_SUPPORT_AGENT")
        return "EMOTIONAL_SUPPORT_AGENT"

    def _build_messages(
        self,
        agent_name: str,
        user_message: str,
        chat_history: List[Dict],
        rag_context: str,
        user_context: Dict | None,
        risk_level: str,
    ) -> List[Dict[str, str]]:
        """Construct the message list for the Groq API call."""
        agent_instructions = AGENT_INSTRUCTIONS_MAP[agent_name]

        # System prompt = global rules + agent-specific instructions
        system_content = f"{GLOBAL_RULES}\n\n{'='*60}\n\n{agent_instructions}"

        # Add RAG context
        if rag_context:
            system_content += (
                f"\n\n{'='*60}\n"
                "TRUSTED KNOWLEDGE BASE CONTEXT (use this to ground your response):\n"
                f"{rag_context}\n"
                "Base your response on this context where relevant. "
                "Do not invent statistics or make unsupported claims."
            )

        # Add user context (name, mood, etc.)
        if user_context:
            user_ctx_str = "\n".join(f"- {k}: {v}" for k, v in user_context.items() if v)
            if user_ctx_str:
                system_content += f"\n\nUSER CONTEXT:\n{user_ctx_str}"

        # Risk level guidance
        if risk_level == "high":
            system_content += "\n\n[CRITICAL: The user's message contains HIGH-RISK language. Follow all crisis protocols immediately. Safety first.]"
        elif risk_level == "moderate":
            system_content += "\n\n[NOTE: Moderate distress indicators detected. Be extra gentle and check in on safety.]"

        messages = [{"role": "system", "content": system_content}]

        # Add recent chat history (up to 10 turns)
        for msg in chat_history[-10:]:
            if msg.get("role") in ("user", "assistant"):
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current message
        messages.append({"role": "user", "content": user_message})

        return messages

    @staticmethod
    def _summarize_history(history: List[Dict], max_turns: int = 3) -> str:
        """Create a brief summary of recent chat history for the router."""
        if not history:
            return "No previous messages"
        recent = history[-max_turns * 2:]
        return " | ".join(
            f"{m['role']}: {m['content'][:80]}…" if len(m['content']) > 80 else f"{m['role']}: {m['content']}"
            for m in recent
            if m.get("role") in ("user", "assistant")
        )
