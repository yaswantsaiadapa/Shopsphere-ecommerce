# __init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Setup upload folder
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    with app.app_context():
        # Import models here to avoid circular imports
        from .models import User, Product, CartItem, Sale
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Register blueprints
        from .routes import main, auth, customer, admin
        app.register_blueprint(main)
        app.register_blueprint(auth, url_prefix='/auth')
        app.register_blueprint(customer, url_prefix='/customer')
        app.register_blueprint(admin, url_prefix='/admin')
        
        # Create database tables
        try:
            db.create_all()
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    return app