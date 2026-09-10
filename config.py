"""
config.py — Application configuration for MindGuard
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///instance/mindguard.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Groq
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = "llama3-70b-8192"
    GROQ_FAST_MODEL = "llama3-8b-8192"

    # Demo / Mock mode
    DEMO_MODE = os.environ.get("DEMO_MODE", "False").lower() == "true"

    # RAG
    FAISS_INDEX_PATH = os.environ.get("FAISS_INDEX_PATH", "instance/faiss_index")
    EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    KNOWLEDGE_BASE_DIR = "knowledge_base"
    RAG_TOP_K = 4

    # Session / Security
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_ENABLED = True

    # Chat
    MAX_CHAT_HISTORY = int(os.environ.get("MAX_CHAT_HISTORY", 20))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
