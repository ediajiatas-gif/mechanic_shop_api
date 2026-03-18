from app.extensions import ma
from app.models import Inventory, db

        
class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        include_relationships = True
        load_instance = True  # tells Marshmallow to create Customer objects
        sqla_session = db.session  # required when using load_instance=True
        
    # service_tickets = ma.auto_field(dump_only=True)
inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)