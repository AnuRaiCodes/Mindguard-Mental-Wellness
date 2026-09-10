"""
tests/test_safety.py — Tests for the safety layer
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from safety import check_risk_level, build_safe_response, sanitize_response


def test_high_risk_detection():
    text = "I want to kill myself tonight"
    risk_level, crisis_needed = check_risk_level(text)
    assert risk_level == "high"
    assert crisis_needed is True


def test_high_risk_no_reason_to_live():
    text = "I have no reason to live anymore"
    risk_level, _ = check_risk_level(text)
    assert risk_level == "high"


def test_moderate_risk_detection():
    text = "I feel completely hopeless and worthless"
    risk_level, _ = check_risk_level(text)
    assert risk_level == "moderate"


def test_low_risk():
    text = "I am feeling a bit stressed about my exams"
    risk_level, crisis_needed = check_risk_level(text)
    assert risk_level == "low"
    assert crisis_needed is False


def test_build_safe_response_high():
    response = build_safe_response("test response", "high")
    assert "iCall" in response
    assert "9152987821" in response


def test_build_safe_response_low():
    response = build_safe_response("test response", "low")
    assert response == "test response"


def test_sanitize_response_safe():
    clean = sanitize_response("Here are some breathing exercises you can try.")
    assert "breathing exercises" in clean


def test_burden_language_high_risk():
    text = "everyone would be better off without me"
    risk_level, crisis_needed = check_risk_level(text)
    assert risk_level == "high"
    assert crisis_needed is True


def test_empty_text_low_risk():
    risk_level, crisis_needed = check_risk_level("")
    assert risk_level == "low"
    assert crisis_needed is False
