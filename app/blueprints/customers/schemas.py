from app.extensions import ma
from app.models import Customer, db

        
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_relationships = True
        load_instance = True  # tells Marshmallow to create Customer objects
        sqla_session = db.session  # required when using load_instance=True
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)