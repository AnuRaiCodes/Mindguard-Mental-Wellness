"""
routes/dashboard.py — Dashboard route
"""
from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from models import db, MoodEntry, ChatSession, JournalEntry, WellnessGoal

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    # Mood stats (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    mood_entries = (
        MoodEntry.query
        .filter(MoodEntry.user_id == current_user.id, MoodEntry.created_at >= seven_days_ago)
        .order_by(MoodEntry.created_at.asc())
        .all()
    )

    avg_mood = None
    if mood_entries:
        avg_mood = round(sum(e.mood_score for e in mood_entries) / len(mood_entries), 1)

    # Mood chart data
    mood_chart_labels = [e.created_at.strftime("%b %d") for e in mood_entries]
    mood_chart_data = [e.mood_score for e in mood_entries]

    # Recent chat sessions
    recent_chats = (
        ChatSession.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(ChatSession.updated_at.desc())
        .limit(5)
        .all()
    )

    # Journal count
    journal_count = JournalEntry.query.filter_by(user_id=current_user.id).count()

    # Active wellness goals
    active_goals = (
        WellnessGoal.query
        .filter_by(user_id=current_user.id, is_active=True)
        .all()
    )

    # Latest mood entry
    latest_mood = (
        MoodEntry.query
        .filter_by(user_id=current_user.id)
        .order_by(MoodEntry.created_at.desc())
        .first()
    )

    return render_template(
        "dashboard/index.html",
        avg_mood=avg_mood,
        mood_entries=mood_entries,
        mood_chart_labels=mood_chart_labels,
        mood_chart_data=mood_chart_data,
        recent_chats=recent_chats,
        journal_count=journal_count,
        active_goals=active_goals,
        latest_mood=latest_mood,
    )
