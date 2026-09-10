"""
routes/chat.py — Chat routes and agent API endpoint
"""
import json
import logging
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from models import db, ChatSession, ChatMessage
from groq_client import get_groq_client
from rag.pipeline import get_rag_pipeline
from agents.orchestrator import Orchestrator

logger = logging.getLogger(__name__)
chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


def get_orchestrator():
    from flask import current_app
    groq = get_groq_client(current_app._get_current_object())
    rag = get_rag_pipeline(current_app._get_current_object())
    return Orchestrator(groq, rag)


@chat_bp.route("/")
@login_required
def index():
    sessions = (
        ChatSession.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(ChatSession.updated_at.desc())
        .limit(20)
        .all()
    )
    return render_template("chat/index.html", sessions=sessions)


@chat_bp.route("/session/new", methods=["POST"])
@login_required
def new_session():
    session = ChatSession(user_id=current_user.id, title="New Conversation")
    db.session.add(session)
    db.session.commit()
    return jsonify({"session_id": session.id})


@chat_bp.route("/session/<int:session_id>")
@login_required
def session_view(session_id):
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    messages = session.messages.all()
    return render_template("chat/session.html", session=session, messages=messages)


@chat_bp.route("/session/<int:session_id>/messages")
@login_required
def get_messages(session_id):
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    messages = [m.to_dict() for m in session.messages.all()]
    return jsonify({"messages": messages})


@chat_bp.route("/send", methods=["POST"])
@login_required
def send_message():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    user_message = (data.get("message") or "").strip()
    session_id = data.get("session_id")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Get or create session
    if session_id:
        chat_session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    else:
        chat_session = None

    if not chat_session:
        chat_session = ChatSession(user_id=current_user.id, title=user_message[:60])
        db.session.add(chat_session)
        db.session.flush()

    # Build chat history for context
    history_msgs = chat_session.messages.order_by(ChatMessage.timestamp).all()
    chat_history = [
        {"role": m.role, "content": m.content}
        for m in history_msgs[-20:]
        if m.role in ("user", "assistant")
    ]

    # User context
    user_context = {
        "name": current_user.display_name or current_user.username,
        "age_group": current_user.age_group,
    }

    # Save user message
    user_msg = ChatMessage(
        session_id=chat_session.id,
        role="user",
        content=user_message,
    )
    db.session.add(user_msg)

    # Process through orchestrator
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.process(user_message, chat_history, user_context)
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        result = {
            "response": "I'm having a momentary issue. Please try again, or if you're in crisis, please call iCall at 9152987821.",
            "agent_used": "EMOTIONAL_SUPPORT_AGENT",
            "agent_display_name": "Emotional Support Agent",
            "agent_icon": "💚",
            "risk_level": "low",
            "crisis_resources_needed": False,
            "rag_context_used": False,
        }

    # Save assistant message
    ai_msg = ChatMessage(
        session_id=chat_session.id,
        role="assistant",
        content=result["response"],
        agent_used=result["agent_used"],
        risk_flag=result["risk_level"] == "high",
    )
    db.session.add(ai_msg)

    # Update session title if first message
    if len(history_msgs) == 0:
        chat_session.title = user_message[:60]

    db.session.commit()

    return jsonify({
        "response": result["response"],
        "session_id": chat_session.id,
        "agent_used": result["agent_used"],
        "agent_display_name": result["agent_display_name"],
        "agent_icon": result["agent_icon"],
        "risk_level": result["risk_level"],
        "crisis_resources_needed": result["crisis_resources_needed"],
        "message_id": ai_msg.id,
    })


@chat_bp.route("/session/<int:session_id>/delete", methods=["POST"])
@login_required
def delete_session(session_id):
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    session.is_active = False
    db.session.commit()
    return jsonify({"success": True})
