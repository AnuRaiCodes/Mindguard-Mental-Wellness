"""
routes/auth.py — Authentication routes
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ─── Forms ────────────────────────────────────────────────────────────────────

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 64)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    display_name = StringField("Display Name", validators=[Length(0, 100)])
    age_group = SelectField("Age Group", choices=[
        ("", "Prefer not to say"),
        ("under-18", "Under 18"),
        ("18-25", "18–25"),
        ("26-35", "26–35"),
        ("36-50", "36–50"),
        ("50+", "50+"),
    ])
    password = PasswordField("Password", validators=[DataRequired(), Length(8, 128)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    consent = BooleanField("I understand this is a wellness companion, not a substitute for professional mental health care.", validators=[DataRequired()])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Email already registered.")


class LoginForm(FlaskForm):
    username = StringField("Username or Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")


# ─── Routes ───────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            display_name=form.display_name.data.strip() or form.username.data.strip(),
            age_group=form.age_group.data,
            consent_given=form.consent.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username.data.strip()
        user = (
            User.query.filter_by(username=identifier).first()
            or User.query.filter_by(email=identifier.lower()).first()
        )
        if user and user.check_password(form.password.data):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.display_name or user.username}! 💚", "success")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Invalid credentials. Please try again.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out. Take care! 💚", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return render_template("landing.html")
