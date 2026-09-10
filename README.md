# MindGuard — AI-Powered Mental Health Awareness & Suicide Prevention App

> **⚠️ Important Disclaimer:** MindGuard is a wellness awareness companion and is **not a substitute for professional mental health care**. If you are in crisis, please call **iCall: 9152987821** or **Vandrevala Foundation: 1860-2662-345** (24/7, FREE). Emergency: **112**.

---

## 🧠 Overview

MindGuard is a complete, production-ready AI-powered mental health awareness and suicide prevention web application built with:

- **Python Flask** — Backend framework
- **Groq API** (Llama 3) — LLM for AI conversations
- **RAG + FAISS** — Retrieval-Augmented Generation with FAISS vector database
- **Multi-Agent Architecture** — Orchestrator + 4 specialized agents
- **Bootstrap 5** — Responsive UI
- **SQLite/SQLAlchemy** — Database
- **Flask-Login + Flask-WTF** — Authentication & security

---

## 🏗️ Architecture

```
User → Orchestrator/Router → Specialized Agent → RAG (FAISS) → Groq API → Safety Check → Response
```

### Multi-Agent System

| Agent | Role |
|-------|------|
| 🧠 **Awareness Agent** | Mental health education, psychoeducation, stigma reduction |
| 💚 **Emotional Support Agent** | Empathetic listening, validation, emotional support |
| 🛡️ **Safety & Wellbeing Agent** | Crisis detection, suicide prevention, safety protocols |
| 🌱 **Prevention & Wellness Agent** | Coping strategies, mindfulness, professional resources |

### Safety Flow
```
User Message → Keyword Safety Pre-Check → Orchestrator → Agent → RAG Retrieval → 
Groq LLM → Sanitize Response → Safety Post-Check → Final Response
```

---

## ✨ Features

- 💬 **AI Mental Health Chatbot** — Multi-agent AI with empathetic, safe conversations
- 📊 **Mood Tracker** — Log and visualize mood and energy trends
- ✍️ **Guided Journal** — Private journaling with therapeutic writing prompts
- 🎯 **Wellness Goals** — Set and track personal wellness objectives
- 🧘 **Mindfulness Guidance** — Breathing exercises, meditation, yoga tips
- 📋 **Distress Screening** — PHQ-9 and GAD-7 awareness self-assessments
- 🆘 **Crisis Resources** — Verified Indian helplines always accessible
- 🔐 **User Profiles** — Personal settings, privacy controls, data deletion
- 🛡️ **Safety Layer** — Real-time risk detection and crisis protocol
- 📚 **RAG Knowledge Base** — Grounded in trusted mental health resources

---

## 🚀 Quick Start

### 1. Clone and navigate
```bash
cd mindguard_app
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux
```

Edit `.env`:
```env
SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key   # Get free at https://console.groq.com
DEMO_MODE=False                   # Set True to run without API key
```

### 5. Run the application
```bash
python run.py
```

Open **http://localhost:5000** in your browser.

---

## 🔑 Getting a Free Groq API Key

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Create an API key
4. Add to your `.env` file: `GROQ_API_KEY=your-key-here`

---

## 🎭 Demo Mode (No API Key Required)

Set `DEMO_MODE=True` in `.env` to run with pre-written demo responses. Perfect for local testing and college demos without needing an API key.

---

## 🧪 Running Tests

```bash
# From the mindguard_app directory
pytest tests/ -v

# Run specific test files
pytest tests/test_safety.py -v
pytest tests/test_app.py -v
pytest tests/test_rag.py -v
```

---

## 📁 Project Structure

```
mindguard_app/
├── app.py                    # Flask application factory
├── run.py                    # Entry point
├── config.py                 # Configuration classes
├── models.py                 # SQLAlchemy database models
├── safety.py                 # Safety layer (risk detection)
├── groq_client.py            # Groq API integration
├── requirements.txt
├── .env.example
│
├── agents/
│   ├── __init__.py
│   ├── instructions.py       # ⭐ EDITABLE agent instructions & behavior
│   └── orchestrator.py       # Multi-agent orchestrator/router
│
├── rag/
│   ├── __init__.py
│   └── pipeline.py           # FAISS RAG pipeline
│
├── knowledge_base/           # Trusted mental health documents
│   ├── mental_health_basics.txt
│   ├── coping_strategies.txt
│   ├── mindfulness_wellness.txt
│   ├── suicide_prevention.txt
│   └── resources_helplines.txt
│
├── routes/
│   ├── auth.py               # Authentication
│   ├── chat.py               # Chat & agent API
│   ├── dashboard.py          # Dashboard
│   ├── mood.py               # Mood tracking
│   ├── journal.py            # Journal
│   ├── profile.py            # User profile & settings
│   ├── resources.py          # Helplines & resources
│   └── api.py                # General API endpoints
│
├── templates/                # Jinja2 HTML templates
├── static/                   # CSS, JS, images
├── tests/                    # Test suite
└── instance/                 # SQLite DB & FAISS index (auto-created)
```

---

## 🎨 Customizing Agent Behavior

Edit `agents/instructions.py` to customize:

- Agent personalities and tone
- Safety rules and crisis handling protocols
- Cultural considerations (Indian context)
- Response styles and formats
- What each agent can/cannot do
- Routing logic

---

## 🔐 Security Features

- **Flask-WTF CSRF** protection on all forms
- **Flask-Bcrypt** password hashing
- **Flask-Login** session management
- **Input validation** with WTForms
- **SQL injection prevention** via SQLAlchemy ORM
- **Safety layer** with regex-based risk detection
- **Response sanitization** before delivery
- **Privacy controls** — users can delete all data

---

## 🏥 Helplines Reference

| Organization | Number | Hours |
|-------------|--------|-------|
| iCall (TISS) | 9152987821 | Mon–Sat, 8am–10pm |
| Vandrevala Foundation | 1860-2662-345 | 24/7, FREE |
| AASRA | 9820466627 | 24/7 |
| Emergency | 112 | 24/7 |

---

## 🚢 Production Deployment

```bash
# Using Gunicorn
gunicorn "app:create_app('production')" --bind 0.0.0.0:8000 --workers 4

# Environment
FLASK_ENV=production
SESSION_COOKIE_SECURE=True
SECRET_KEY=<strong-random-key>
```

---

## 📜 Ethical Guidelines & Disclaimers

1. MindGuard **cannot diagnose** any mental health condition
2. MindGuard **cannot predict** suicide risk
3. MindGuard is **not a replacement** for professional mental health care
4. Information provided is for **awareness and education only**
5. Always refer users to qualified professionals for clinical assessment
6. Safe messaging guidelines are followed for suicide/self-harm topics

---

## 🎓 College Project Notes

This project demonstrates:
- **Agentic AI** with multi-agent orchestration
- **RAG** (Retrieval-Augmented Generation) with FAISS
- **Groq API** integration (Llama 3 models)
- **Full-stack Flask** development
- **Responsible AI** — safety, ethics, and safe messaging
- **Database design** with SQLAlchemy
- **Authentication** and **privacy controls**

---

*Built with ❤️ for mental health awareness*
