from flask import Blueprint

mechanic_bp = Blueprint("mechanics_bp", __name__)

from . import routes