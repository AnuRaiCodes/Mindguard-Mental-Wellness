"""
routes/journal.py — Journal tracking routes
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange

from models import db, JournalEntry

journal_bp = Blueprint("journal", __name__, url_prefix="/journal")


class JournalForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 200)])
    content = TextAreaField("Journal Entry", validators=[DataRequired(), Length(1, 10000)])
    mood_score = IntegerField("Mood Score", validators=[NumberRange(1, 10)], default=5)
    tags = StringField("Tags (comma-separated)", validators=[Length(0, 300)])
    is_private = BooleanField("Keep Private", default=True)


@journal_bp.route("/")
@login_required
def index():
    entries = (
        JournalEntry.query
        .filter_by(user_id=current_user.id)
        .order_by(JournalEntry.created_at.desc())
        .all()
    )
    form = JournalForm()
    return render_template("journal/index.html", entries=entries, form=form)


@journal_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_entry():
    form = JournalForm()
    if form.validate_on_submit():
        tags = ",".join(t.strip() for t in form.tags.data.split(",") if t.strip())
        entry = JournalEntry(
            user_id=current_user.id,
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            mood_score=form.mood_score.data,
            tags=tags,
            is_private=form.is_private.data,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Journal entry saved! ✍️", "success")
        return redirect(url_for("journal.index"))
    return render_template("journal/new_entry.html", form=form)


@journal_bp.route("/view/<int:entry_id>")
@login_required
def view_entry(entry_id):
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    return render_template("journal/view_entry.html", entry=entry)


@journal_bp.route("/edit/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    form = JournalForm(obj=entry)
    if form.validate_on_submit():
        entry.title = form.title.data.strip()
        entry.content = form.content.data.strip()
        entry.mood_score = form.mood_score.data
        entry.tags = ",".join(t.strip() for t in form.tags.data.split(",") if t.strip())
        entry.is_private = form.is_private.data
        db.session.commit()
        flash("Entry updated!", "success")
        return redirect(url_for("journal.index"))
    return render_template("journal/edit_entry.html", form=form, entry=entry)


@journal_bp.route("/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete_entry(entry_id):
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted.", "info")
    return redirect(url_for("journal.index"))


@journal_bp.route("/prompts")
@login_required
def prompts():
    """Return writing prompts for journaling."""
    prompts_list = [
        "What emotions am I carrying with me today, and what might they be telling me?",
        "Describe one small moment today that brought you comfort or joy.",
        "What is one challenge I'm facing, and what small step can I take toward it?",
        "Who are three people I'm grateful for, and why?",
        "What would I tell a close friend going through what I'm experiencing?",
        "What is draining my energy right now, and what is restoring it?",
        "What does rest look like for me? When did I last truly rest?",
        "What am I proud of myself for recently — no matter how small?",
        "What boundary do I need to set or reinforce in my life right now?",
        "If I could speak to my past self from one year ago, what would I say?",
        "What does 'good enough' look like for me today?",
        "What fear am I carrying, and what evidence do I have that I can handle it?",
    ]
    import random
    return jsonify({"prompt": random.choice(prompts_list)})
