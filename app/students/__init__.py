from flask import Blueprint

student_bp = Blueprint(
    "student",
    __name__,
    template_folder="templates",
    static_folder="../static"
)

# Import routes after bp is defined
from . import controller