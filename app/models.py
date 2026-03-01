from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association table for Many-to-Many between service_tickets and mechanics
service_mechanics = db.Table(
    'service_mechanics',
    db.Column('ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'), primary_key=True)
)

# ------------------ Models ---------------------

# Customer model
class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    phone = db.Column(db.String(50), nullable=False)

    # One-to-many relationship: Customer → ServiceTickets
    service_tickets = db.relationship(
        "ServiceTicket", back_populates="customer", cascade="all, delete-orphan"
    )

# ServiceTicket model
class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(50), nullable=False)  # Vehicle Identification Number
    
    # timestamp of when the service was requested; set automatically if not provided
    service_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    service_desc = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))

    # Relationships
    customer = db.relationship("Customer", back_populates="service_tickets")
    mechanics = db.relationship(
        "Mechanic", secondary=service_mechanics, back_populates="service_tickets"
    )

# Mechanic model
class Mechanic(db.Model):
    __tablename__ = "mechanics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    phone = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Float, nullable=False)

    # Many-to-Many: Mechanics ↔ ServiceTickets
    service_tickets = db.relationship(
        "ServiceTicket", secondary=service_mechanics, back_populates="mechanics"
    )