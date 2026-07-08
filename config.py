import os # allows us to reach into devlopment enviornment 
class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mechanic_shop.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = '300'

#For testing our data     
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'

class ProductionConfig:
    # Get database URI from environment variable
    _database_uri = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///mechanic_shop.db')
    
    # Handle PostgreSQL SSL for Render
    if _database_uri and _database_uri.startswith('postgresql'):
        # Add SSL mode for PostgreSQL connections
        SQLALCHEMY_DATABASE_URI = _database_uri + '?sslmode=require'
    else:
        SQLALCHEMY_DATABASE_URI = _database_uri
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    CACHE_TYPE = 'SimpleCache'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Prevent stale/dropped connections on Render's free-tier Postgres
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }