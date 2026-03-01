from .schemas import customer_schema, customers_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, db
from . import customer_bp


# Get Customers
@customer_bp.route("/", methods=['GET'])
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    
                                   # turns object into dictionary
    return jsonify(customers_schema.dump(customers)), 200

# Get a specific customer by ID
@customer_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)  # Get customer by primary key
    if not customer:
        return jsonify({"error": "Customer not found"}), 404  # 404 if no customer
    
    return jsonify(customer_schema.dump(customer)), 200  # Convert to dict and return JSON

# Create Customer
@customer_bp.route("/", methods=['POST'])  # Creates API endpoint
def create_customer():  # Function that runs when the endpoint is called
    try:  # Validates Data
        customer_data = customer_schema.load(request.json)  # takes JSON from request and validates with Marshmallow
    except ValidationError as e:
        return jsonify(e.messages), 400  # if validation fails, return error message

    # Check if email already exists
    query = select(Customer).where(Customer.email == customer_data.email)  # checks db for Customer with this email
    existing_customer = db.session.execute(query).scalars().all()  # runs query to get matching customers
    if existing_customer:  # blocks request if email already exists
        return jsonify({"error": "Email already associated with an account."}), 400  # Client error

    # Save the new customer object directly (customer_data is already a Customer object)
    db.session.add(customer_data)
    db.session.commit()  # Save customer to db

    return jsonify(customer_schema.dump(customer_data)), 201  # returns customer as JSON with 201 Resource created

# Update Customer by Id
@customer_bp.route("/<int:customer_id>", methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404  # 404 if no customer
    
    try:
        customer_update = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Only updates the fields that were sent
    for attr in ['name', 'email', 'phone']:     # only updates the new values
        if getattr(customer_update, attr, None) is not None:
            setattr(customer, attr, getattr(customer_update, attr))
        
    db.session.commit()
    return jsonify(customer_schema.dump(customer)), 200
        
# Delete Customer
@customer_bp.route("/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {customer_id}, successfully deleted'}), 200