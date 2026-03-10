from .schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, db, ServiceTicket
from app.blueprints.service_tickets.schemas import service_tickets_schema
from . import customer_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required

# Login Route for Customers
@customer_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.get_json())
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query =select(Customer).where(Customer.email == email) 
    customer = db.session.execute(query).scalar_one_or_none() #Query customer table for a customer with this email

    if customer and customer.password == password: #if we have a customer associated with the customername, validate the password
        token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "token": token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401

# Get tickets for the authenticated customer
@customer_bp.route("/my-tickets", methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    query = select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    tickets = db.session.execute(query).scalars().all()
    return jsonify(service_tickets_schema.dump(tickets)), 200

# Get Customers
@customer_bp.route("/", methods=['GET'])
# @cache.cached(timeout=60)
def get_customers():
    # handle pagination parameters safely
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', type=int)
    query = select(Customer)

    if page and per_page:
        paged = db.paginate(query, page=page, per_page=per_page)
        return jsonify(customers_schema.dump(paged.items)), 200

    # fallback: return all records
    customers = db.session.execute(query).scalars().all()
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
@limiter.limit("5 per day") # Client can only attempt to create 3 users per hour
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
@token_required
def update_customer(customer_id, user_id=None):
    # customer_id comes from the URL
    # user_id comes from the token if you want to use it
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        customer_update = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for attr in ['name', 'email', 'phone', 'password']:
        if getattr(customer_update, attr, None) is not None:
            setattr(customer, attr, getattr(customer_update, attr))

    db.session.commit()
    return jsonify(customer_schema.dump(customer)), 200
        
# Delete Customer
@customer_bp.route("/", methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {customer_id}, successfully deleted'}), 200