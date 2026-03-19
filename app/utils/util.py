from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify
import os
                                            # Temp secret key for Github Test Cases
SECRET_KEY = os.environ.get('SECRET_KEY') or "super secret secrets"

# Updated token_required decorator (Option 1)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Look for the token in the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Pass user_id as a keyword argument
            kwargs['user_id'] = data['sub']  
            
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401

        # Call the route with all args and kwargs
        return f(*args, **kwargs)

    return decorated

def encode_token(user_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(user_id)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token