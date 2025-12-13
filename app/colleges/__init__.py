from flask import Blueprint

college_bp = Blueprint(
    "college",
    __name__,
    template_folder="templates",
    static_folder="../static"
)

# Import routes after bp is defined
from . import controller
