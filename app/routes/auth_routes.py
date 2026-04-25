from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models.user import User

auth = Blueprint("auth", __name__)

# Register
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        university = request.form["university"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        user = User(
            full_name=full_name,
            email=email,
            password=hashed_password,
            university=university
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# Login
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user:
            #check banned user
            if hasattr(user, "is_banned") and user.is_banned:
                flash("Your account has been baned.", "danger")
                return redirect(url_for("auth.login"))
            
            #check password
            if check_password_hash(user.password, password):
                login_user(user)
                flash("Login successful.", "success")
                return redirect(url_for("auth.dashboard"))
            
        flash("Invalid credentials.", "danger")

    return render_template("login.html")


# Dashboard
@auth.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


# Logout
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("main.home"))