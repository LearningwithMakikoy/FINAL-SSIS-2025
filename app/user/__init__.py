# app/user/__init__.py
from flask import Blueprint

bp = Blueprint(
    "user",
    __name__,
    template_folder="templates",
    static_folder="../static"
)

# Import routes after bp is defined
from . import controller
