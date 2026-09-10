"""
routes/mood.py — Mood tracking routes
"""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

from models import db, MoodEntry

mood_bp = Blueprint("mood", __name__, url_prefix="/mood")

MOOD_LABELS = {
    1: "Very Low", 2: "Low", 3: "Down", 4: "Slightly Low", 5: "Neutral",
    6: "Okay", 7: "Good", 8: "Great", 9: "Very Good", 10: "Excellent"
}

EMOTION_OPTIONS = [
    "Happy", "Sad", "Anxious", "Calm", "Angry", "Excited", "Frustrated",
    "Hopeful", "Lonely", "Grateful", "Overwhelmed", "Content", "Tired",
    "Nervous", "Confident", "Peaceful", "Worried", "Joyful", "Depressed",
]


@mood_bp.route("/")
@login_required
def index():
    entries = (
        MoodEntry.query
        .filter_by(user_id=current_user.id)
        .order_by(MoodEntry.created_at.desc())
        .limit(30)
        .all()
    )

    # Chart data — last 14 days
    fourteen_days_ago = datetime.utcnow() - timedelta(days=14)
    chart_entries = (
        MoodEntry.query
        .filter(MoodEntry.user_id == current_user.id, MoodEntry.created_at >= fourteen_days_ago)
        .order_by(MoodEntry.created_at.asc())
        .all()
    )

    chart_labels = [e.created_at.strftime("%b %d") for e in chart_entries]
    chart_data = [e.mood_score for e in chart_entries]
    energy_data = [e.energy_level for e in chart_entries]

    return render_template(
        "mood/index.html",
        entries=entries,
        chart_labels=chart_labels,
        chart_data=chart_data,
        energy_data=energy_data,
        emotion_options=EMOTION_OPTIONS,
        mood_labels=MOOD_LABELS,
    )


@mood_bp.route("/log", methods=["POST"])
@login_required
def log_mood():
    data = request.get_json() or request.form

    try:
        mood_score = int(data.get("mood_score", 5))
        energy_level = int(data.get("energy_level", 5))
        sleep_hours = float(data.get("sleep_hours", 0.0))
        emotions = data.get("emotions", "")
        if isinstance(emotions, list):
            emotions = ",".join(emotions)
        notes = (data.get("notes") or "").strip()

        mood_score = max(1, min(10, mood_score))
        energy_level = max(1, min(10, energy_level))
        sleep_hours = max(0, min(24, sleep_hours))

        entry = MoodEntry(
            user_id=current_user.id,
            mood_score=mood_score,
            mood_label=MOOD_LABELS.get(mood_score, ""),
            emotions=emotions,
            energy_level=energy_level,
            sleep_hours=sleep_hours,
            notes=notes,
        )
        db.session.add(entry)
        db.session.commit()

        if request.is_json:
            return jsonify({"success": True, "entry": entry.to_dict()})
        flash("Mood logged! 📊", "success")
        return redirect(url_for("mood.index"))
    except (ValueError, TypeError) as e:
        if request.is_json:
            return jsonify({"error": str(e)}), 400
        flash("Invalid mood data.", "danger")
        return redirect(url_for("mood.index"))


@mood_bp.route("/data")
@login_required
def mood_data():
    """API endpoint for mood chart data."""
    days = int(request.args.get("days", 14))
    days = min(days, 90)
    since = datetime.utcnow() - timedelta(days=days)

    entries = (
        MoodEntry.query
        .filter(MoodEntry.user_id == current_user.id, MoodEntry.created_at >= since)
        .order_by(MoodEntry.created_at.asc())
        .all()
    )

    return jsonify({
        "labels": [e.created_at.strftime("%b %d") for e in entries],
        "mood": [e.mood_score for e in entries],
        "energy": [e.energy_level for e in entries],
        "entries": [e.to_dict() for e in entries],
    })


@mood_bp.route("/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete_entry(entry_id):
    entry = MoodEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"success": True})
