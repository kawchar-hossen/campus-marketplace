from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.user import User

auth = Blueprint("auth", __name__)


# =====================================
# Register
# =====================================
@auth.route("/register", methods=["GET", "POST"])
def register():

    # If already logged in
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        university = request.form.get("university", "").strip()

        # -------------------------
        # Validation
        # -------------------------
        if not full_name or not email or not password or not university:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("auth.register"))

        # -------------------------
        # Check duplicate email
        # -------------------------
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("auth.login"))

        # -------------------------
        # Create user
        # -------------------------
        hashed_password = generate_password_hash(password)

        user = User(
            full_name=full_name,
            email=email,
            password=hashed_password,
            university=university,
            profile_image="default.png",
            is_admin=False,
            is_banned=False
        )

        db.session.add(user)

        try:
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("auth.login"))

        except IntegrityError:
            db.session.rollback()
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register"))

    return render_template("register.html")


# =====================================
# Login
# =====================================
@auth.route("/login", methods=["GET", "POST"])
def login():

    # Already logged in
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        next_page = request.args.get("next")

        if not email or not password:
            flash("Email and password required.", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()

        if user:

            # banned check
            if hasattr(user, "is_banned") and user.is_banned:
                flash("Your account has been banned.", "danger")
                return redirect(url_for("auth.login"))

            # password check
            if check_password_hash(user.password, password):
                login_user(user)

                flash("Login successful.", "success")

                if next_page:
                    return redirect(next_page)

                return redirect(url_for("auth.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# =====================================
# Dashboard
# =====================================
@auth.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        user=current_user
    )


# =====================================
# Logout
# =====================================
@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "info")

    return redirect(url_for("main.home"))