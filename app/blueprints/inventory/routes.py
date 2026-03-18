from .schemas import inventory_schema, inventories_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Inventory, db
from . import inventory_bp
from app.extensions import limiter, cache
from app.utils.util import token_required

# Get Parts within Inventory
@inventory_bp.route("/", methods=['GET'])
# @cache.cached(timeout=60)
def get_parts():
    # handle pagination parameters safely
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', type=int)
    query = select(Inventory)

    if page and per_page:
        paged = db.paginate(query, page=page, per_page=per_page)
        return jsonify(inventories_schema.dump(paged.items)), 200

    # fallback: return all records
    parts = db.session.execute(query).scalars().all()
    return jsonify(inventories_schema.dump(parts)), 200


# Create Part
@inventory_bp.route("/", methods=['POST'])  # Creates API endpoint
# @limiter.limit("5 per day") # Client can only attempt to create t parts per hour
def create_part():  # Function that runs when the endpoint is called
    try:  # Validates Data
        inventory_data = inventory_schema.load(request.json)  # takes JSON from request and validates with Marshmallow
    except ValidationError as e:
        print(e.messages)
        return jsonify(e.messages), 400  # if validation fails, return error message

    # Check if part already exists
    query = select(Inventory).where(Inventory.part_name == inventory_data.part_name)  # checks db for Part with this name
    existing_part = db.session.execute(query).scalars().all()  # runs query to get matching parts
    if existing_part:  # blocks request if part name already exists
        return jsonify({"error": "Part already exists."}), 400  # Client error

    # Save the new part object directly (inventory_data is already a Invetory object)
    db.session.add(inventory_data)
    db.session.commit()  # Save part to db

    return jsonify(inventory_schema.dump(inventory_data)), 201  # returns part as JSON with 201 Resource created

# Update Part by Id
@inventory_bp.route("/<int:part_id>", methods=['PUT'])
# @token_required
def update_part(part_id):
    part = db.session.get(Inventory, part_id)
    
    if not part:
        return jsonify({"error": "Part not found"}), 404  # 404 if no part
    
    try:
        part_update = inventory_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Only updates the fields that were sent
    for attr in ['part_name', 'price']:     # only updates the new values
        if getattr(part_update, attr, None) is not None:
            setattr(part, attr, getattr(part_update, attr))
        
    db.session.commit()
    return jsonify(inventory_schema.dump(part)), 200
        
# Delete part
@inventory_bp.route("/<int:part_id>", methods=['DELETE'])
# @token_required
def delete_part(part_id):
    part = db.session.get(Inventory, part_id)
    
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f'Part: {part_id}, successfully deleted'}), 200