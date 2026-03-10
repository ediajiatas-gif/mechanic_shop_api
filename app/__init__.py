from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from .extensions import ma, limiter, cache # relative import since were already in app folder
from .models import db
from .blueprints.customers import customer_bp
from .blueprints.mechanics import mechanic_bp
from .blueprints.service_tickets import service_ticket_bp
from .blueprints.inventory import inventory_bp

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'  # Our API URL (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic Shop API"
    }
    
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")
    
    #Initialize Extensions
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    #Register Blueprints
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventories')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL) #Registering our swagger BP
    
    
    return app
# Function that produces Flask App