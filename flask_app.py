from app import create_app
from app.models import db
import os

app = create_app('ProductionConfig') 

# Create table
with app.app_context():
    try:
        # db.drop_all() 
        db.create_all()
    except Exception as e:
        print(f"Database initialization warning: {e}")
        # Don't crash on database errors - tables may already exist on Render

#gunicorn flask_app:app (differentiates flask_app and app folder)