from flask import Blueprint

inventory_bp = Blueprint("invetories_bp", __name__)

from . import routes