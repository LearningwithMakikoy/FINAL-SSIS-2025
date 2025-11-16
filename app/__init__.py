# app/__init__.py
import os
from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
from .database import get_connection
from app.models import User  # your psycopg2-compatible User class

# Load environment variables from .env
load_dotenv()

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = "user.login"  # redirect unauthorized users

def create_app():
    """App factory function for Flask app using psycopg2 (no SQLAlchemy)"""
    app = Flask(__name__, template_folder="templates", static_folder="static")

# CONFIGURATION 
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

#  LOGIN MANAGER 
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # fetch user from database using psycopg2
        return User.get_by_id(user_id)

#  BLUEPRINTS
    from .user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix="/user")

# MAIN ROUTES 
    @app.route("/")
    def home():
        return render_template("index.html")

    return app
