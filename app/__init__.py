# app/__init__.py
import os
from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
from app.models import User  # psycopg2 model

# Load environment variables
load_dotenv()

# Initialize LoginManager (global)
login_manager = LoginManager()
login_manager.login_view = "user.login"   # redirect if not logged in


def create_app():
    """App factory using psycopg2 (no SQLAlchemy)."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # ---- CONFIG ----
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    # ---- LOGIN MANAGER ----
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # ---- BLUEPRINTS ----
    from .user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix="/user")

    # ---- MAIN ROUTE ----
    @app.route("/")
    def home():
        return render_template("index.html")

    return app
