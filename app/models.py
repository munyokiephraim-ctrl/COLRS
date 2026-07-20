from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='student')
    points_balance = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    is_available = db.Column(db.Boolean, default=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    points_redeemed = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='Placed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True)
    transactions = db.relationship('LoyaltyTransaction', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey('orders.id'),
        nullable=False
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey('menu_items.id'),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    unit_price = db.Column(
        db.Float,
        nullable=False
    )

    item = db.relationship(
        "MenuItem",
        backref="order_items"
    )

class LoyaltyTransaction(db.Model):
    __tablename__ = 'loyalty_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    transaction_type = db.Column(db.String(10), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)