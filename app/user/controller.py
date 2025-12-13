from flask import render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import bp
from .forms import SignupForm, LoginForm
from .models import User


# DASHBOARD / HOME
@bp.route('/')
@login_required
def index():
    return render_template('index.html')

# AUTH ROUTES
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        password = form.password.data

        # Check if username exists
        existing = User.get_by_username(username)
        if existing:
            flash("Username already taken", "danger")
            return redirect(url_for('user.signup'))
        
        #Check if email exist
        existing_email = User.get_by_email(email)
        if existing_email:
            flash("Email address already registered", "danger")
            return redirect(url_for('user.signup'))

        # Create user
        hashed_pw = generate_password_hash(password)
        new_user = User.create(username, email, hashed_pw)

        flash("Account created! You may now log in.", "success")
        return redirect(url_for('user.login'))

    return render_template('signup.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        user = User.get_by_username(username)

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for('user.login'))

        login_user(user)
        flash("Logged in successfully!", "success")
        return redirect(url_for('user.index'))

    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('user.login'))



