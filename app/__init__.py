import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # 1. FIXED SECRET KEY: Prevents session cookies from breaking on every restart/push
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'colrs-secure-static-fallback-key-2026')
    
    # 2. DATABASE CONFIGURATION: Handles Railway PostgreSQL or local fallback safely
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Railway sometimes uses 'postgres://' which SQLAlchemy requires to be 'postgresql://'
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///colrs.db'
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Import models so SQLAlchemy registers them
    from app.models import User, MenuItem, Order, OrderItem, LoyaltyTransaction

    @login_manager.user_loader
    chno = lambda user_id: User.query.get(int(user_id))

    # Register Blueprints (Connecting Auth, Student, and Admin)
    from app.auth.routes import auth_bp
    from app.student.routes import student_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Create tables automatically if they don't exist
    with app.app_context():
        db.create_all()

    return app