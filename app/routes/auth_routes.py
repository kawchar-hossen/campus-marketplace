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
from app.utils.token import generate_reset_token
from app.utils.token import verify_reset_token
from flask_mail import Message
from app import mail
from app.utils.otp import generate_otp
from app.utils.otp import verify_otp as check_otp
from flask import session
import re


auth = Blueprint("auth", __name__)


def is_strong_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least 1 uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least 1 lowercase letter."

    if not re.search(r"[0-9]", password):
        return "Password must contain at least 1 number."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least 1 special character."

    return None

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
        confirm_password = request.form.get("confirm_password", "").strip()
        university = request.form.get("university", "").strip()

        # -------------------------
        # Validation
        # -------------------------
        if not full_name or not email or not password or not university:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        # 🔥 MATCH CHECK (ADD HERE)
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        error = is_strong_password(password)

        if error:
            flash(error, "danger")
            return redirect(url_for("auth.register"))
        
        # -------------------------
        # Check duplicate email
        # -------------------------
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("auth.login"))

        # 🔥 1. Generate OTP
        otp = generate_otp(email)

        # 🔥 2. Send OTP email
        try:
            msg = Message(
                subject="Your OTP Verification Code",
                recipients=[email]
            )

            msg.body = f"""
Hi {full_name},

Your OTP for registration is: {otp}

This OTP is valid for 5 minutes.
"""

            mail.send(msg)

        except Exception as e:
            print("EMAIL ERROR:", e)
            flash("Failed to send OTP email.", "danger")
            return redirect(url_for("auth.register"))

        # 🔥 3. Store temp user (IMPORTANT)
        session["temp_user"] = {
            "full_name": full_name,
            "email": email,
            "password": generate_password_hash(password),
            "university": university
        }

        flash("OTP sent to your email!", "success")
        return redirect(url_for("auth.verify_otp"))

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


# =====================================
# Change Password
# =====================================
@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form.get("current_password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # -------------------------
        # Validation
        # -------------------------
        if not current_password or not new_password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.change_password"))

        # Check current password
        if not check_password_hash(current_user.password, current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("auth.change_password"))

        # New password match check
        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("auth.change_password"))

        # Password length check
        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("auth.change_password"))

        # Prevent same password reuse
        if check_password_hash(current_user.password, new_password):
            flash("New password cannot be the same as current password.", "warning")
            return redirect(url_for("auth.change_password"))

        # -------------------------
        # Update Password
        # -------------------------
        current_user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("Password changed successfully.", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("change_password.html")


# =====================================
# Forgot Password
# =====================================
@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Please enter your email.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found with this email.", "warning")
            return redirect(url_for("auth.forgot_password"))

        # ✅ Generate token
        token = generate_reset_token(user.email)

        reset_link = url_for(
            "auth.reset_password",
            token=token,
            _external=True
        )

        # ✅ SEND REAL EMAIL
        try:
            msg = Message(
                subject="Password Reset Request",
                recipients=[user.email]
            )

            msg.body = f"""
Hi {user.full_name},

You requested a password reset.

Click the link below to reset your password:
{reset_link}

If you did not request this, ignore this email.
"""

            mail.send(msg)

            flash("Reset link sent to your email!", "success")

        except Exception as e:
            print("EMAIL ERROR:", e)
            flash("Email sending failed. Check server config.", "danger")

        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")

# =====================================
# reset password
# =====================================

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    email = verify_reset_token(token)

    if not email:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    if request.method == "POST":
        new_password = request.form.get("password", "").strip()

        if len(new_password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(request.url)

        user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("Password reset successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")


# =====================================
# verify otp
# =====================================
@auth.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    temp_user = session.get("temp_user")

    if not temp_user:
        flash("Session expired. Please register again.", "danger")
        return redirect(url_for("auth.register"))

    if request.method == "POST":

        user_otp = request.form.get("otp")

        email = temp_user["email"]

        if check_otp(email, user_otp):

            # Create user only after OTP success
            user = User(
                full_name=temp_user["full_name"],
                email=temp_user["email"],
                password=temp_user["password"],
                university=temp_user["university"],
                profile_image="default.png",
                is_admin=False,
                is_banned=False
            )

            db.session.add(user)
            db.session.commit()

            session.pop("temp_user", None)

            flash("Account verified successfully!", "success")
            return redirect(url_for("auth.login"))

        else:
            flash("Invalid or expired OTP.", "danger")

    return render_template("verify_otp.html")