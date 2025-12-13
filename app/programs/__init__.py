from flask import Blueprint

program_bp = Blueprint(
    "program",
    __name__,
    template_folder="templates",
    static_folder="../static"
)

# Import routes after bp is defined
from . import controller
