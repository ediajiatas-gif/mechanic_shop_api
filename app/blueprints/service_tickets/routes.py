from .schemas import (service_ticket_schema, service_tickets_schema, create_service_ticket_schema, edit_mechanics_schema,)
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import ServiceTicket, Mechanic, Inventory, db
from . import service_ticket_bp
from app.extensions import cache
from app.utils.util import token_required


# Get all service tickets
@service_ticket_bp.route("/", methods=['GET'])
@cache.cached(timeout=60)
def get_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()
    return jsonify(service_tickets_schema.dump(tickets)), 200


# Create a service ticket
@service_ticket_bp.route("/", methods=['POST'])
def create_ticket():
    try:
        ticket_data = create_service_ticket_schema.load(request.json)
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
@token_required
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

@service_ticket_bp.route("/<int:service_ticket_id>", methods=['PUT'])
def edit_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    try:
        ticket_data = service_ticket_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Update allowed fields
    for attr in ['vin', 'service_date', 'service_desc', 'customer_id']:
        if getattr(ticket_data, attr, None) is not None:
            setattr(service_ticket, attr, getattr(ticket_data, attr))

    db.session.commit()
    return jsonify(service_ticket_schema.dump(service_ticket)), 200


# Edit mechanics on a ticket: add and remove mechanics by id
@service_ticket_bp.route("/<int:ticket_id>/edit", methods=['PUT'])
def edit_ticket_mechanics(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    try:
        payload = edit_mechanics_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(e.messages), 400

    add_ids = payload.get('add_ids', [])
    remove_ids = payload.get('remove_ids', [])

    # Add mechanics
    for mech_id in add_ids:
        try:
            mech_id = int(mech_id)
        except (TypeError, ValueError):
            continue
        mechanic = db.session.get(Mechanic, mech_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    # Remove mechanics
    for mech_id in remove_ids:
        try:
            mech_id = int(mech_id)
        except (TypeError, ValueError):
            continue
        mechanic = db.session.get(Mechanic, mech_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200

# Add single part to a service ticket
@service_ticket_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=['PUT'])
@token_required
def add_part_to_ticket(ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(Inventory, part_id)
    
    if not ticket or not part:
        return jsonify({"error": "Service ticket or part not found"}), 404
    
    #Prevent duplicate parts
    if part in ticket.parts:
        return jsonify({"error": "Part already added to this ticket"}), 400
    
    ticket.parts.append(part)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200