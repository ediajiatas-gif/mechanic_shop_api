from app import create_app
from app.models import db
import os

app = create_app('ProductionConfig') 

# Create table
with app.app_context():
    # db.drop_all() 
    db.create_all()

# ------------------ Run App ---------------------
if __name__ == '__main__':
    # Get port from environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    # Use debug mode only in development (when DEBUG env var is set)
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)

#gunicorn flask_app:app (differentiates flask_app and app folder)