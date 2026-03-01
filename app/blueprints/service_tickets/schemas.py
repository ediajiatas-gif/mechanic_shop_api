from app.extensions import ma
from app.models import ServiceTicket, db

        
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        include_relationships = True
        load_instance = True  # tells Marshmallow to create ServiceTicket objects
        sqla_session = db.session  # required when using load_instance=True
        
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)