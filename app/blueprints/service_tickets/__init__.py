from flask import Blueprint

service_ticket_bp = Blueprint("service_tickets_bp", __name__)

from . import routes