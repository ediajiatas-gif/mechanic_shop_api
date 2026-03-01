from app.extensions import ma
from app.models import Mechanic, db

        
class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        include_relationships = True
        load_instance = True  # tells Marshmallow to create Customer objects
        sqla_session = db.session  # required when using load_instance=True
        
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)