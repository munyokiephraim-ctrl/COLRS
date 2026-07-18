from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='Student')
    # Loyalty engine field for upcoming Sprint 3 integration
    loyalty_points = db.Column(db.Integer, default=0)

class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=False) # e.g., "Main Cafeteria, North Wing"
    # Relationship allows easy access to all items in a specific restaurant
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy=True)

class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    # Dietary tags stored as a string (e.g., "Vegan,Gluten-Free,Keto") 
    # This enables the efficient filtering required for your system development
    dietary_tags = db.Column(db.String(200), nullable=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

    def has_tag(self, tag):
        """Helper method to check if an item matches a specific diet tag."""
        if not self.dietary_tags:
            return False
        return tag.lower() in [t.strip().lower() for t in self.dietary_tags.split(',')]