from app import create_app, db
from app.models import User, MenuItem, Order, OrderItem, LoyaltyTransaction

app = create_app()

with app.app_context():
    print("Generating database tables...")
    db.create_all()
    print("Database initialized successfully! 'colrs.db' has been created.")