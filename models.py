"""
models.py — SQLAlchemy database models for MindGuard
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


# ─────────────────────────── USER ───────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # Profile
    display_name = db.Column(db.String(100), default="")
    age_group = db.Column(db.String(20), default="")       # e.g. "18-25"
    preferred_language = db.Column(db.String(10), default="en")
    bio = db.Column(db.Text, default="")
    avatar_color = db.Column(db.String(10), default="#6c757d")

    # Privacy & Consent
    consent_given = db.Column(db.Boolean, default=False)
    data_retention_days = db.Column(db.Integer, default=90)
    share_anonymous_data = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    chat_sessions = db.relationship("ChatSession", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    mood_entries = db.relationship("MoodEntry", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    journal_entries = db.relationship("JournalEntry", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    wellness_goals = db.relationship("WellnessGoal", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


# ─────────────────────────── CHAT ───────────────────────────────────────────

class ChatSession(db.Model):
    __tablename__ = "chat_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(120), default="New Conversation")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship("User", back_populates="chat_sessions")
    messages = db.relationship("ChatMessage", back_populates="session", lazy="dynamic",
                                cascade="all, delete-orphan", order_by="ChatMessage.timestamp")

    def __repr__(self):
        return f"<ChatSession {self.id} user={self.user_id}>"


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("chat_sessions.id"), nullable=False)
    role = db.Column(db.String(10), nullable=False)          # "user" | "assistant" | "system"
    content = db.Column(db.Text, nullable=False)
    agent_used = db.Column(db.String(40), default="")        # which agent responded
    risk_flag = db.Column(db.Boolean, default=False)         # high-risk message flag
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship("ChatSession", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "agent_used": self.agent_used,
            "risk_flag": self.risk_flag,
            "timestamp": self.timestamp.isoformat(),
        }


# ─────────────────────────── MOOD ───────────────────────────────────────────

class MoodEntry(db.Model):
    __tablename__ = "mood_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)        # 1–10
    mood_label = db.Column(db.String(30), default="")         # "Happy", "Anxious", etc.
    emotions = db.Column(db.String(200), default="")          # comma-separated tags
    energy_level = db.Column(db.Integer, default=5)           # 1–10
    sleep_hours = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="mood_entries")

    def to_dict(self):
        return {
            "id": self.id,
            "mood_score": self.mood_score,
            "mood_label": self.mood_label,
            "emotions": self.emotions.split(",") if self.emotions else [],
            "energy_level": self.energy_level,
            "sleep_hours": self.sleep_hours,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }


# ─────────────────────────── JOURNAL ────────────────────────────────────────

class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), default="Journal Entry")
    content = db.Column(db.Text, nullable=False)
    mood_score = db.Column(db.Integer, default=5)
    tags = db.Column(db.String(300), default="")
    is_private = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="journal_entries")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "mood_score": self.mood_score,
            "tags": self.tags.split(",") if self.tags else [],
            "is_private": self.is_private,
            "created_at": self.created_at.isoformat(),
        }


# ─────────────────────────── WELLNESS GOALS ─────────────────────────────────

class WellnessGoal(db.Model):
    __tablename__ = "wellness_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    category = db.Column(db.String(50), default="")          # sleep, exercise, mindfulness, etc.
    target_days = db.Column(db.Integer, default=7)
    completed_days = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="wellness_goals")


# ─────────────────────────── SCREENING ──────────────────────────────────────

class RiskScreening(db.Model):
    __tablename__ = "risk_screenings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    screening_type = db.Column(db.String(30), default="phq9")   # phq9 / gad7 / general
    responses = db.Column(db.Text, default="{}")                 # JSON string
    risk_level = db.Column(db.String(20), default="low")         # low / moderate / high
    score = db.Column(db.Integer, default=0)
    recommendations = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")
