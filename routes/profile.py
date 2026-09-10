"""
routes/profile.py — User profile and settings routes
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import Length, NumberRange

from models import db, User, WellnessGoal, MoodEntry, JournalEntry, ChatSession

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


class ProfileForm(FlaskForm):
    display_name = StringField("Display Name", validators=[Length(0, 100)])
    age_group = SelectField("Age Group", choices=[
        ("", "Prefer not to say"),
        ("under-18", "Under 18"),
        ("18-25", "18–25"),
        ("26-35", "26–35"),
        ("36-50", "36–50"),
        ("50+", "50+"),
    ])
    bio = TextAreaField("About Me", validators=[Length(0, 500)])
    preferred_language = SelectField("Language", choices=[
        ("en", "English"),
        ("hi", "Hindi"),
        ("ta", "Tamil"),
        ("te", "Telugu"),
        ("kn", "Kannada"),
        ("mr", "Marathi"),
        ("bn", "Bengali"),
    ])
    share_anonymous_data = BooleanField("Allow anonymous usage data to improve MindGuard")
    data_retention_days = IntegerField("Data Retention (days)", validators=[NumberRange(7, 365)], default=90)


@profile_bp.route("/")
@login_required
def index():
    form = ProfileForm(obj=current_user)
    goals = WellnessGoal.query.filter_by(user_id=current_user.id, is_active=True).all()
    mood_count = MoodEntry.query.filter_by(user_id=current_user.id).count()
    journal_count = JournalEntry.query.filter_by(user_id=current_user.id).count()
    chat_count = ChatSession.query.filter_by(user_id=current_user.id).count()

    return render_template(
        "profile/index.html",
        form=form,
        goals=goals,
        mood_count=mood_count,
        journal_count=journal_count,
        chat_count=chat_count,
    )


@profile_bp.route("/update", methods=["POST"])
@login_required
def update_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.display_name = form.display_name.data.strip()
        current_user.age_group = form.age_group.data
        current_user.bio = form.bio.data.strip()
        current_user.preferred_language = form.preferred_language.data
        current_user.share_anonymous_data = form.share_anonymous_data.data
        current_user.data_retention_days = form.data_retention_days.data
        db.session.commit()
        flash("Profile updated! ✅", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    return redirect(url_for("profile.index"))


@profile_bp.route("/goals/add", methods=["POST"])
@login_required
def add_goal():
    data = request.get_json() or request.form
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Title required"}), 400

    goal = WellnessGoal(
        user_id=current_user.id,
        title=title,
        description=(data.get("description") or "").strip(),
        category=(data.get("category") or "").strip(),
        target_days=int(data.get("target_days", 7)),
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify({"success": True, "goal_id": goal.id})


@profile_bp.route("/goals/<int:goal_id>/complete", methods=["POST"])
@login_required
def complete_goal_day(goal_id):
    goal = WellnessGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    goal.completed_days = min(goal.completed_days + 1, goal.target_days)
    if goal.completed_days >= goal.target_days:
        goal.is_active = False
    db.session.commit()
    return jsonify({"success": True, "completed_days": goal.completed_days})


@profile_bp.route("/delete-data", methods=["POST"])
@login_required
def delete_all_data():
    """Privacy feature — delete all user data."""
    uid = current_user.id
    MoodEntry.query.filter_by(user_id=uid).delete()
    JournalEntry.query.filter_by(user_id=uid).delete()
    ChatSession.query.filter_by(user_id=uid).delete()
    WellnessGoal.query.filter_by(user_id=uid).delete()
    db.session.commit()
    flash("All your data has been deleted. Your account remains active.", "info")
    return redirect(url_for("profile.index"))
