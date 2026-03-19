from app import create_app
from app.models import db

app = create_app('ProductionConfig') 

# Create table
with app.app_context():
    # db.drop_all() 
    db.create_all()

# ------------------ Run App ---------------------
    # app.run() - no longer required because of gunicorn

#gunicorn flask_app:app (differntiates flask_app and app folder)