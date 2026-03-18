from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models import Mechanic, db
from . import mechanic_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required


# Get mechanics
@mechanic_bp.route("/", methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
                                   # turns object into dictionary
    return jsonify(mechanics_schema.dump(mechanics)), 200

# Get a specific mechanic by ID
@mechanic_bp.route("/<int:mechanic_id>", methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)  # Get mechanic by primary key
    if not mechanic:
        return jsonify({"error": "mechanic not found"}), 404  # 404 if no mechanic
    
    return jsonify(mechanic_schema.dump(mechanic)), 200  # Convert to dict and return JSON

# Create mechanic
@mechanic_bp.route("/", methods=['POST'])  # Creates API endpoint
@limiter.limit("5 per day")
def create_mechanic():  # Function that runs when the endpoint is called
    try:  # Validates Data
        mechanic_data = mechanic_schema.load(request.json)  # takes JSON from request and validates with Marshmallow
    except ValidationError as e:
        return jsonify(e.messages), 400  # if validation fails, return error message

    # Check if email already exists
    query = select(Mechanic).where(Mechanic.email == mechanic_data.email)  # checks db for mechanic with this email
    existing_mechanic = db.session.execute(query).scalars().all()  # runs query to get matching mechanics
    if existing_mechanic:  # blocks request if email already exists
        return jsonify({"error": "Email already associated with an account."}), 400  # Client error

    # Save the new mechanic object directly (mechanic_data is already a mechanic object)
    db.session.add(mechanic_data)
    db.session.commit()  # Save mechanic to db

    return jsonify(mechanic_schema.dump(mechanic_data)), 201  # returns mechanic as JSON with 201 Resource created

# Update mechanic by Id
@mechanic_bp.route("/<int:mechanic_id>", methods=['PUT'])
# @token_required
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic:
        return jsonify({"error": "mechanic not found"}), 404  # 404 if no mechanic
    
    try:
        mechanic_update = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Only updates the fields that were sent
    for attr in ['name', 'email', 'phone', 'salary']:     # only updates the new values
        if getattr(mechanic_update, attr, None) is not None:
            setattr(mechanic, attr, getattr(mechanic_update, attr))
        
    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic)), 200
        
# Delete mechanic
@mechanic_bp.route("/<int:mechanic_id>", methods=['DELETE'])
# @token_required
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic:
        return jsonify({"error": "mechanic not found"}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f'mechanic id: {mechanic_id}, successfully deleted'}), 200

# Returns list of mechanics  in order of who has worked on the most tickets
@mechanic_bp.route("/most_tickets", methods=['GET'])
def get_mechanics_by_ticket_count():
    
    query = select(Mechanic).options(selectinload(Mechanic.service_tickets))
    mechanics = db.session.execute(query).scalars().all()
    
    # Sort mechanics by the number of service tickets using a lambda function
    mechanics = sorted(mechanics, key=lambda mechanic: len(mechanic.service_tickets), reverse=True)
    
    return jsonify(mechanics_schema.dump(mechanics)), 200

# Get Mechanic by Name
@mechanic_bp.route("/search", methods=['GET'])
def search_mechanic():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Name parameter is required"}), 400
    
    query = select(Mechanic).where(Mechanic.name.ilike(f'%{name}%')).options(selectinload(Mechanic.service_tickets))
    mechanics = db.session.execute(query).scalars().all()
    
    if not mechanics:
        return jsonify({"message": f"No mechanics found with name containing '{name}'"}), 404
    
    return jsonify(mechanics_schema.dump(mechanics)), 200