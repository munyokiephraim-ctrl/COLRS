from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models import MenuItem, Order, OrderItem, LoyaltyTransaction

student_bp = Blueprint('student', __name__)

@student_bp.route('/menu')
@login_required
def menu():
    category = request.args.get('category', 'All')
    if category and category != 'All':
        items = MenuItem.query.filter_by(category=category, is_available=True).all()
    else:
        items = MenuItem.query.filter_by(is_available=True).all()
        
    categories = ['All', 'Mains', 'Snacks', 'Drinks', 'Desserts']
    return render_template('student/menu.html', items=items, categories=categories, active_category=category)

@student_bp.route('/cart/add/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    item = MenuItem.query.get_or_404(item_id)
    cart = session.get('cart', {})
    
    str_id = str(item_id)
    if str_id in cart:
        cart[str_id]['quantity'] += 1
    else:
        cart[str_id] = {
            'name': item.name,
            'price': float(item.price),
            'quantity': 1
        }
        
    session['cart'] = cart
    flash(f'Added {item.name} to your cart!', 'success')
    return redirect(url_for('student.menu'))

@student_bp.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    
    # Points calculation: 10 points = 1 KSh discount (or adjust per your project spec)
    points_discount = 0
    use_points = request.args.get('use_points', 'false') == 'true'
    if use_points and current_user.points_balance >= 50:
        points_discount = current_user.points_balance / 10.0 # example valuation
        if points_discount > subtotal:
            points_discount = subtotal

    total = subtotal - points_discount
    return render_template('student/cart.html', cart=cart, subtotal=subtotal, total=total, points_discount=points_discount)

@student_bp.route('/order/place', methods=['POST'])
@login_required
def place_order():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('student.menu'))
        
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    
    # Create the Order
    new_order = Order(
        user_id=current_user.id,
        total_amount=subtotal,
        status='Placed'
    )
    db.session.add(new_order)
    db.session.commit() # Commits to get order_id
    
    # Create Order Items
    for item_id, details in cart.items():
        order_item = OrderItem(
            order_id=new_order.id,
            item_id=int(item_id),
            quantity=details['quantity'],
            unit_price=details['price']
        )
        db.session.add(order_item)
        
    # Loyalty Points Engine: 1 point per 10 KSh spent[cite: 1]
    earned_points = int(subtotal // 10)
    current_user.points_balance += earned_points
    
    # Log the loyalty transaction
    loyalty_tx = LoyaltyTransaction(
        user_id=current_user.id,
        order_id=new_order.id,
        transaction_type='Credit',
        points=earned_points
    )
    db.session.add(loyalty_tx)
    db.session.commit()
    
    # Clear cart session
    session.pop('cart', None)
    
    flash(f'Order placed successfully! You earned +{earned_points} loyalty points.', 'success')
    return redirect(url_for('student.order_confirmation', order_id=new_order.id))

@student_bp.route('/order/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('student/confirmation.html', order=order)