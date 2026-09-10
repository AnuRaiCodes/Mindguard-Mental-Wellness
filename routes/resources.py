"""
routes/resources.py — Mental health resources and helplines
"""
from flask import Blueprint, render_template
from flask_login import login_required

resources_bp = Blueprint("resources", __name__, url_prefix="/resources")

HELPLINES = [
    {
        "name": "iCall (TISS Mumbai)",
        "number": "9152987821",
        "description": "Professional counseling, specializes in student mental health. Free/low-cost.",
        "hours": "Mon–Sat, 8am–10pm",
        "url": "https://icallhelpline.org",
        "category": "counseling",
    },
    {
        "name": "Vandrevala Foundation",
        "number": "1860-2662-345",
        "description": "Free 24/7 mental health helpline. Confidential support for all.",
        "hours": "24/7, FREE",
        "url": "https://vandrevalafoundation.com",
        "category": "crisis",
    },
    {
        "name": "AASRA",
        "number": "9820466627",
        "description": "Suicide prevention and emotional support helpline.",
        "hours": "24/7",
        "url": "http://www.aasra.info",
        "category": "crisis",
    },
    {
        "name": "Snehi",
        "number": "044-24640050",
        "description": "Emotional support and suicide prevention (Chennai).",
        "hours": "Available daily",
        "url": None,
        "category": "crisis",
    },
    {
        "name": "Fortis Stress Helpline",
        "number": "8376804102",
        "description": "Psychological support for stress and mental health concerns.",
        "hours": "Available",
        "url": None,
        "category": "counseling",
    },
    {
        "name": "NIMHANS Bangalore",
        "number": "080-46110007",
        "description": "National Institute of Mental Health and Neurosciences.",
        "hours": "Office hours",
        "url": "https://nimhans.ac.in",
        "category": "professional",
    },
    {
        "name": "Parivarthan Counselling",
        "number": "+91-7676602602",
        "description": "Counseling and psychotherapy services.",
        "hours": "Mon–Sat",
        "url": "https://parivarthan.org",
        "category": "counseling",
    },
    {
        "name": "Emergency Services",
        "number": "112",
        "description": "For immediate danger to life — police, ambulance, fire.",
        "hours": "24/7",
        "url": None,
        "category": "emergency",
    },
]

ONLINE_RESOURCES = [
    {
        "name": "The Mind Clan",
        "url": "https://themindclan.com",
        "description": "Verified directory of mental health professionals in India.",
    },
    {
        "name": "YourDOST",
        "url": "https://yourdost.com",
        "description": "Online emotional wellness platform with counselors.",
    },
    {
        "name": "Wysa",
        "url": "https://wysa.io",
        "description": "AI-powered mental health app with therapist option.",
    },
    {
        "name": "Insight Timer",
        "url": "https://insighttimer.com",
        "description": "Free guided meditation and mindfulness app.",
    },
    {
        "name": "NIMHANS Digital Academy",
        "url": "https://nimhansdigitalacademy.in",
        "description": "Free mental health education resources from NIMHANS.",
    },
]


@resources_bp.route("/")
@login_required
def index():
    return render_template(
        "resources/index.html",
        helplines=HELPLINES,
        online_resources=ONLINE_RESOURCES,
    )
