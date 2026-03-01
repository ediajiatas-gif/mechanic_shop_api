from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import ServiceTicket, Mechanic, db
from . import service_ticket_bp


# Get all service tickets
@service_ticket_bp.route("/", methods=['GET'])
def get_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()
    return jsonify(service_tickets_schema.dump(tickets)), 200


# Create a service ticket
@service_ticket_bp.route("/", methods=['POST'])
def create_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # ensure the ticket has a timestamp; model default will handle it,
    # but set explicitly in case marshmallow cleared it earlier
    from datetime import datetime
    if not getattr(ticket_data, 'service_date', None):
        ticket_data.service_date = datetime.utcnow()

    db.session.add(ticket_data)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket_data)), 201


# Assign a mechanic to a service ticket
@service_ticket_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Service ticket or mechanic not found"}), 404

    # Prevent duplicate assignment
    if mechanic in ticket.mechanics:
        return jsonify({"error": "Mechanic already assigned to this ticket"}), 400

    ticket.mechanics.append(mechanic)
    db.session.commit()

    return jsonify(service_ticket_schema.dump(ticket)), 200


# Remove a mechanic from a service ticket
@service_ticket_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Service ticket or mechanic not found"}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"error": "Mechanic not assigned to this ticket"}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()

    return jsonify(service_ticket_schema.dump(ticket)), 200