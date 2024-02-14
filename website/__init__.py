"""
This script sets up a Flask application for an academy management system.

It includes:
- Flask app initialization with secret key and database configuration.
- SQLAlchemy integration for managing the SQLite database.
- Flask-Login setup for user authentication.
- Blueprint registration for organizing routes.
- Database creation upon app context creation.
- Definition of a user loader function for Flask-Login.

Functions:
- create_app(): Initializes the Flask application with necessary configurations.
- create_database(app): Creates the SQLite database if it doesn't exist.

Modules Imported:
- Flask: For creating the web application.
- SQLAlchemy: For database management.
- path from os: For file path operations.
- LoginManager from flask_login: For user authentication.
"""

# Import necessary modules
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Create SQLAlchemy database instance
db = SQLAlchemy()

# Define the name of the SQLite database
DB_NAME = "academy.db"

def create_app():
    """
    Initializes the Flask application with necessary configurations.

    Returns:
        Flask: Initialized Flask application.
    """
    # Initialize Flask app
    app = Flask(__name__)

    # Set secret key for session management
    app.config['SECRET_KEY'] = 'owenvwvibwecnaxcdibvccan'

    # Set database URI for SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)
    
    # Import views and authentication blueprints
    from .views import views
    from .auth import auth
    
    # Register blueprints with app
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    # Import models
    from .models import User, Booking, Weekly_menu, Access_Card, Reminder, Booking_Modification_Log
    
    # Create database tables within app context
    with app.app_context():
        db.create_all()
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        """
        User loader function for Flask-Login.

        Args:
            id (int): User ID.

        Returns:
            User: User object corresponding to the given ID.
        """
        return User.query.get(int(id))
    
    # Return the initialized app
    return app
     

def create_database(app):
    """
    Creates the SQLite database if it doesn't exist.

    Args:
        app (Flask): Flask application.

    Returns:
        None
    """
    if not path.exists('website/' + DB_NAME):
        # Create all database tables within app context
        db.create_all(app=app)
        print('Created Database!')
