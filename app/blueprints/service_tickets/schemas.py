from app.extensions import ma
from app.models import ServiceTicket, db
from marshmallow import fields

        
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        include_relationships = True
        load_instance = True  # tells Marshmallow to create ServiceTicket objects
        sqla_session = db.session  # required when using load_instance=True

class CreateServiceTicketSchema(ServiceTicketSchema):
    class Meta:
        exclude = ('mechanics',)  # Exclude mechanics from creation
        model = ServiceTicket
        include_relationships = True
        load_instance = True
        sqla_session = db.session

class EditTicketSchema(ma.Schema): #for book ids we want to add/remove
    add_ticket_ids = fields.List(fields.Int(), required=True)
    remove_ticket_ids = fields.List(fields.Int(), required=True)
    
    class Meta:
        fields = ("add_ticket_ids", "remove_ticket_ids")


class EditMechanicsSchema(ma.Schema):
    add_ids = fields.List(fields.Int(), required=False)
    remove_ids = fields.List(fields.Int(), required=False)

    class Meta:
        fields = ("add_ids", "remove_ids")
        
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
create_service_ticket_schema = CreateServiceTicketSchema()
# Return schema: use the same ServiceTicketSchema (no invalid excludes)
return_ticket_schema = ServiceTicketSchema()
edit_ticket_schema = EditTicketSchema()
edit_mechanics_schema = EditMechanicsSchema()
