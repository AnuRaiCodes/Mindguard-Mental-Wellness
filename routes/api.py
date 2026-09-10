"""
routes/api.py — General API endpoints (screening, wellness, etc.)
"""
import json
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from models import db, RiskScreening

api_bp = Blueprint("api", __name__, url_prefix="/api")

# PHQ-9 questions (simplified)
PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things?",
    "Feeling down, depressed, or hopeless?",
    "Trouble falling or staying asleep, or sleeping too much?",
    "Feeling tired or having little energy?",
    "Poor appetite or overeating?",
    "Feeling bad about yourself — or that you're a failure?",
    "Trouble concentrating on things?",
    "Moving or speaking so slowly others have noticed, or being fidgety/restless?",
    "Thoughts that you would be better off dead or hurting yourself in some way?",
]

# GAD-7 questions (simplified)
GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge?",
    "Not being able to stop or control worrying?",
    "Worrying too much about different things?",
    "Trouble relaxing?",
    "Being so restless that it is hard to sit still?",
    "Becoming easily annoyed or irritable?",
    "Feeling afraid as if something awful might happen?",
]


def interpret_phq9(score: int) -> tuple:
    if score <= 4:
        return "minimal", "Your responses suggest minimal depressive symptoms. Keep practicing self-care!"
    elif score <= 9:
        return "mild", "Your responses suggest mild depressive symptoms. Consider speaking with a counselor."
    elif score <= 14:
        return "moderate", "Moderate depressive symptoms noted. Please consider reaching out to a mental health professional."
    elif score <= 19:
        return "moderately-severe", "Moderately severe symptoms noted. Professional support is strongly recommended."
    else:
        return "severe", "Severe symptoms noted. Please reach out to a mental health professional or helpline today."


def interpret_gad7(score: int) -> tuple:
    if score <= 4:
        return "minimal", "Minimal anxiety symptoms. Continue practicing stress management!"
    elif score <= 9:
        return "mild", "Mild anxiety symptoms. Relaxation techniques and self-care can help."
    elif score <= 14:
        return "moderate", "Moderate anxiety symptoms. Consider speaking with a mental health professional."
    else:
        return "severe", "Severe anxiety symptoms. Professional support is strongly recommended."


@api_bp.route("/screening/questions/<screening_type>")
@login_required
def get_questions(screening_type):
    if screening_type == "phq9":
        return jsonify({"questions": PHQ9_QUESTIONS, "scale": "0=Not at all, 1=Several days, 2=More than half the days, 3=Nearly every day"})
    elif screening_type == "gad7":
        return jsonify({"questions": GAD7_QUESTIONS, "scale": "0=Not at all, 1=Several days, 2=More than half the days, 3=Nearly every day"})
    return jsonify({"error": "Unknown screening type"}), 400


@api_bp.route("/screening/submit", methods=["POST"])
@login_required
def submit_screening():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    screening_type = data.get("type", "phq9")
    responses = data.get("responses", {})
    score = sum(int(v) for v in responses.values() if str(v).isdigit())

    if screening_type == "phq9":
        risk_level, recommendation = interpret_phq9(score)
    elif screening_type == "gad7":
        risk_level, recommendation = interpret_gad7(score)
    else:
        return jsonify({"error": "Unknown screening type"}), 400

    screening = RiskScreening(
        user_id=current_user.id,
        screening_type=screening_type,
        responses=json.dumps(responses),
        risk_level=risk_level,
        score=score,
        recommendations=recommendation,
    )
    db.session.add(screening)
    db.session.commit()

    return jsonify({
        "score": score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "screening_id": screening.id,
        "disclaimer": "This screening is for awareness only and is NOT a clinical diagnosis. Please consult a qualified mental health professional for proper assessment.",
    })


@api_bp.route("/wellness/tips")
@login_required
def wellness_tips():
    """Return daily wellness tips."""
    import random
    from datetime import date
    tips = [
        {"title": "Deep Breathing", "content": "Try 4-7-8 breathing: inhale for 4 counts, hold for 7, exhale for 8. Repeat 4 times.", "category": "mindfulness"},
        {"title": "Hydration Check", "content": "Have you had enough water today? Dehydration affects mood and concentration.", "category": "physical"},
        {"title": "5-Minute Walk", "content": "A short walk outside can significantly reduce stress and improve mood.", "category": "physical"},
        {"title": "Gratitude Moment", "content": "Name 3 things you're grateful for today — they can be very small.", "category": "emotional"},
        {"title": "Digital Detox", "content": "Take a 30-minute break from screens. Notice how you feel.", "category": "lifestyle"},
        {"title": "Body Scan", "content": "Close your eyes and slowly scan your body from head to toe. Where are you holding tension? Breathe into that area.", "category": "mindfulness"},
        {"title": "Connect", "content": "Reach out to one friend or family member today, even just to say hello.", "category": "social"},
        {"title": "Sleep Prep", "content": "Set a reminder to start winding down 1 hour before bed. Dim lights and put down screens.", "category": "sleep"},
    ]
    random.seed(date.today().toordinal())
    daily_tip = random.choice(tips)
    return jsonify({"tip": daily_tip})


@api_bp.route("/demo-status")
def demo_status():
    from groq_client import get_groq_client
    from flask import current_app
    client = get_groq_client(current_app._get_current_object())
    return jsonify({"demo_mode": client.is_demo})
