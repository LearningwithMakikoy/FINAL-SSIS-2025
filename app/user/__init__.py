# app/user/__init__.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User  # psycopg2-backed User model
from .forms import LoginForm, SignupForm  # Flask-WTF forms

bp = Blueprint("user", __name__, template_folder="templates", static_folder="../static")

# -------------------------
# USER AUTH ROUTES
# -------------------------

@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("user.index"))  # redirect to dashboard
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)
        User.create(form.username.data, form.email.data, password_hash)
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("user.login"))
    return render_template("signup.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("user.login"))


# -------------------------
# DASHBOARD / INDEX
# -------------------------
@bp.route("/index")
@login_required
def index():
    # No data fetching needed — just render the dashboard with tabs
    return render_template("index.html")
