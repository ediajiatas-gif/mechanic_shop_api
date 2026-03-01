from flask import Blueprint

customer_bp = Blueprint("customers_bp", __name__)

from . import routes