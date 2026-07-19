from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
    
    # Handle PostgreSQL URL format for production
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///colrs.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from app.models import User, MenuItem, Order, OrderItem, LoyaltyTransaction
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    from app.auth.routes import auth_bp
    from app.student.routes import student_bp
    from app.admin.routes import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    with app.app_context():
        db.create_all()
        # Auto-seed default menu items if the table is empty
        if MenuItem.query.count() == 0:
            default_items = [
                MenuItem(name='Espresso Coffee', description='Rich and bold single shot', price=150.0, category='Beverages', is_available=True),
                MenuItem(name='Chicken Burger', description='Juicy grilled chicken patty with lettuce and mayo', price=350.0, category='Meals', is_available=True),
                MenuItem(name='Samosa (2 pcs)', description='Crispy beef or veg triangles', price=100.0, category='Snacks', is_available=True),
                MenuItem(name='Bottled Water', description='500ml refreshing mineral water', price=50.0, category='Beverages', is_available=True)
            ]
            for item in default_items:
                db.session.add(item)
            db.session.commit()
            
    return app