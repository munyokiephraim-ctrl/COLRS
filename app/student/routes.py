from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models import MenuItem, Order, OrderItem, LoyaltyTransaction

student_bp = Blueprint('student', __name__)

@student_bp.before_request
@login_required
def require_student():
    if current_user.role != 'student':
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))

@student_bp.route('/dashboard')
def dashboard():
    # Fetch recent orders for the logged-in student
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('student/dashboard.html', orders=orders)

@student_bp.route('/menu')
def menu():
    category = request.args.get('category', 'All')
    if category and category != 'All':
        items = MenuItem.query.filter_by(category=category, is_available=True).all()
    else:
        items = MenuItem.query.filter_by(is_available=True).all()
        
    # Get unique categories for filtering
    categories = db.session.query(MenuItem.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('student/menu.html', items=items, categories=categories, active_category=category)

@student_bp.route('/cart')
def cart():
    cart_data = session.get('cart', {})
    cart_items = []
    subtotal = 0
    
    for item_id_str, quantity in cart_data.items():
        item = MenuItem.query.get(int(item_id_str))
        if item:
            item_total = float(item.price) * quantity
            subtotal += item_total
            cart_items.append({'item': item, 'quantity': quantity, 'total': item_total})
            
    return render_template('student/cart.html', cart_items=cart_items, subtotal=subtotal)

@student_bp.route('/cart/add/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    item = MenuItem.query.get_or_404(item_id)
    cart = session.get('cart', {})
    
    str_id = str(item_id)
    quantity = int(request.form.get('quantity', 1))
    
    if str_id in cart:
        cart[str_id] += quantity
    else:
        cart[str_id] = quantity
        
    session['cart'] = cart
    flash(f'Added {item.name} to cart!', 'success')
    return redirect(url_for('student.menu'))

@student_bp.route('/checkout', methods=['POST'])
def checkout():
    cart_data = session.get('cart', {})
    if not cart_data:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('student.cart'))
        
    subtotal = 0
    order_items_to_create = []
    
    for item_id_str, quantity in cart_data.items():
        item = MenuItem.query.get(int(item_id_str))
        if item:
            item_total = float(item.price) * quantity
            subtotal += item_total
            order_items_to_create.append({
                'item_id': item.id,
                'quantity': quantity,
                'unit_price': float(item.price)
            })
            
    # Create the Order
    new_order = Order(
        user_id=current_user.id,
        total_amount=subtotal,
        status='Placed'
    )
    db.session.add(new_order)
    db.session.commit()
    
    # Create Order Items
    for oi in order_items_to_create:
        order_item = OrderItem(
            order_id=new_order.id,
            item_id=oi['item_id'],
            quantity=oi['quantity'],
            unit_price=oi['unit_price']
        )
        db.session.add(order_item)
        
    # Award loyalty points (e.g., 10% of total spent or flat points)
    earned_points = int(subtotal * 0.1)
    current_user.points_balance += earned_points
    
    loyalty_tx = LoyaltyTransaction(
        user_id=current_user.id,
        order_id=new_order.id,
        transaction_type='Credit',
        points=earned_points
    )
    db.session.add(loyalty_tx)
    db.session.commit()
    
    # Clear cart
    session.pop('cart', None)
    
    flash(f'Order placed successfully! You earned {earned_points} points.', 'success')
    return redirect(url_for('student.dashboard'))