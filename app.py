import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_for_testing")

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///climate_app.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Maximum content length for file uploads (5MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import the models here
    import models  # noqa: F401
    
    # Create all database tables
    db.create_all()
    
    # Import and register routes
    from routes import *
    
    logger.info("Application initialized successfully")
