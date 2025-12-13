import os
from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
from app.user.models import User


# Load environment variables
load_dotenv()

# Initialize LoginManager (global)
login_manager = LoginManager()
login_manager.login_view = "user.login"   # redirect if not logged in


def create_app():
    """App factory using psycopg2"""
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
    # Import blueprints here to avoid circular imports
    from app.user import bp
    from app.students import student_bp
    from app.colleges import college_bp
    from app.programs import program_bp
  
    
    # Register blueprints with appropriate URL prefixes
    app.register_blueprint(student_bp, url_prefix="/student")      # Routes: /students/*
    app.register_blueprint(college_bp, url_prefix="/college")      # Routes: /colleges/*
    app.register_blueprint(program_bp, url_prefix="/program")      # Routes: /programs/*
    app.register_blueprint(bp, url_prefix="/user")         # Routes: /* (root level)
    

    # ---- MAIN ROUTE ----
    @app.route("/")
    def home():
        return render_template("index.html")

    return app
