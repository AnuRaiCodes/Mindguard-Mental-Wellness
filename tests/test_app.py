"""
tests/test_app.py — Integration tests for Flask routes
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import create_app
from models import db, User


@pytest.fixture
def app():
    app = create_app("development")
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "DEMO_MODE": True,
        "SECRET_KEY": "test-secret-key",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            display_name="Test User",
            consent_given=True,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        return user.id


def login(client, username="testuser", password="password123"):
    return client.post("/auth/login", data={
        "username": username,
        "password": password,
    }, follow_redirects=True)


def test_landing_page(client):
    resp = client.get("/auth/")
    assert resp.status_code == 200


def test_login_page_loads(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    assert b"Sign In" in resp.data


def test_register_page_loads(client):
    resp = client.get("/auth/register")
    assert resp.status_code == 200
    assert b"Create Account" in resp.data


def test_dashboard_requires_auth(client):
    resp = client.get("/dashboard", follow_redirects=False)
    assert resp.status_code in (302, 301)


def test_chat_requires_auth(client):
    resp = client.get("/chat/", follow_redirects=False)
    assert resp.status_code in (302, 301)


def test_mood_requires_auth(client):
    resp = client.get("/mood/", follow_redirects=False)
    assert resp.status_code in (302, 301)


def test_user_registration(client, app):
    resp = client.post("/auth/register", data={
        "username": "newuser",
        "email": "newuser@example.com",
        "display_name": "New User",
        "age_group": "18-25",
        "password": "securepass123",
        "confirm_password": "securepass123",
        "consent": True,
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_user_login(client, test_user, app):
    resp = login(client)
    assert resp.status_code == 200


def test_resources_page_requires_auth(client):
    resp = client.get("/resources/", follow_redirects=False)
    assert resp.status_code in (302, 301)


def test_api_demo_status(client):
    resp = client.get("/api/demo-status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "demo_mode" in data
