from flask import Blueprint, abort
from flask_login import login_required, current_user
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return "<h1>Welcome, Admin! This is your dashboard.</h1>"

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return "<h1>Welcome, Admin! This is your dashboard.</h1>"

@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Security: Ensure only users with the 'Admin' role can access this blueprint
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != 'Admin':
                abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return "<h1>Welcome, Admin! This is your dashboard.</h1>"
    if current_user.role != 'Admin':
        return "Access Denied: Administrative privileges required.", 403


    # Handle adding a new menu item
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')

        if name and price and category:
            new_item = MenuItem(
                name=name,
                description=description,
                price=float(price),
                category=category
            )
            db.session.add(new_item)
            db.session.commit()
            return "Success: Menu item added! <a href='/admin/dashboard'>Return to Dashboard</a>"

    # Fetch live data from database to display on dashboard
    items = MenuItem.query.all()
    orders = Order.query.all()

    # Dynamic fallback UI generation
    items_html = "".join([f"<li><strong>{item.name}</strong> ({item.category}) - KSh {item.price:.2f} <br> <em>{item.description}</em></li><br>" for item in items])
    orders_html = "".join([f"<li>Order #{order.id} | Customer ID: {order.user_id} | Total: KSh {order.total_amount:.2f} | Status: <strong>{order.status}</strong></li>" for order in orders])

    return f'''
        <h2>COLRS - Administrative Dashboard</h2>
        <p>Logged in as: <strong>{current_user.full_name}</strong> | <a href="/auth/logout">Secure Logout</a></p>
        
        <table border="1" cellpadding="10" cellspacing="0" style="width:100%; border-collapse: collapse;">
            <tr>
                <td style="width: 50%; vertical-align: top;">
                    <h3>Add New Menu Item</h3>
                    <form method="POST">
                        <label>Item Name:</label><br>
                        <input type="text" name="name" style="width:80%;" required><br><br>
                        
                        <label>Description / Ingredients:</label><br>
                        <textarea name="description" style="width:80%; height:50px;"></textarea><br><br>
                        
                        <label>Price (KSh):</label><br>
                        <input type="number" step="0.01" name="price" style="width:80%;" required><br><br>
                        
                        <label>Menu Category:</label><br>
                        <select name="category" style="width:84%;">
                            <option value="Mains">Mains</option>
                            <option value="Snacks">Snacks</option>
                            <option value="Drinks">Drinks</option>
                            <option value="Desserts">Desserts</option>
                        </select><br><br>
                        
                        <button type="submit" style="padding: 5px 15px;">Publish to Menu</button>
                    </form>
                </td>
                <td style="width: 50%; vertical-align: top;">
                    <h3>Current Active Menu</h3>
                    <ul>{items_html if items_html else "<li>No items available in the cafeteria database yet.</li>"}</ul>
                </td>
            </tr>
        </table>

        <hr style="margin-top: 30px;">
        <h3>Live Incoming Student Orders</h3>
        <ul>{orders_html if orders_html else "<li>No active customer orders currently placed.</li>"}</ul>
    '''