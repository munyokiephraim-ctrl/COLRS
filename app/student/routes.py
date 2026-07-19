from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import MenuItem, Order, OrderItem, Restaurant, LoyaltyTransaction

student_bp = Blueprint('student', __name__)

@student_bp.route('/menu')
@login_required
def menu():
    available_items = MenuItem.query.all()
    return render_template('student/menu.html', items=available_items, user=current_user)

@student_bp.route('/restaurants')
@login_required
def browse_restaurants():
    restaurants = Restaurant.query.all()
    return render_template('student/restaurants.html', restaurants=restaurants)

@student_bp.route('/cart/add/<int:item_id>')
@login_required
def add_to_cart(item_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    item_id_str = str(item_id)
    if item_id_str in cart:
        cart[item_id_str] += 1
    else:
        cart[item_id_str] = 1
    session['cart'] = cart
    flash('Item added to cart!', 'success')
    return redirect(url_for('student.menu'))

@student_bp.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    subtotal = 0
    for item_id, qty in cart.items():
        item = MenuItem.query.get(int(item_id))
        if item:
            item_total = item.price * qty
            subtotal += item_total
            cart_items.append({'item': item, 'quantity': qty, 'total': item_total})
    return render_template('student/cart.html', cart_items=cart_items, subtotal=subtotal, user=current_user)

@student_bp.route('/order/place', methods=['POST'])
@login_required
def place_order():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('student.menu'))
        
    total_amount = 0
    items_to_process = []
    for item_id, qty in cart.items():
        item = MenuItem.query.get(int(item_id))
        if item:
            total_amount += item.price * qty
            items_to_process.append((item, qty))
            
    # Check for points redemption (Threshold: >= 50 points)
    redeem = request.form.get('redeem_points')
    points_redeemed_count = 0
    discount_amount = 0

    if redeem and (current_user.points_balance or 0) >= 50:
        points_redeemed_count = current_user.points_balance
        discount_amount = points_redeemed_count / 10.0  # 10 points = KSh 1 discount
        
        if discount_amount > total_amount:
            discount_amount = total_amount
            points_redeemed_count = int(discount_amount * 10)

        current_user.points_balance -= points_redeemed_count
        
        # Log debit transaction
        debit_tx = LoyaltyTransaction(
            user_id=current_user.id,
            transaction_type='Debit',
            points=points_redeemed_count
        )
        db.session.add(debit_tx)

    final_amount = total_amount - discount_amount

    new_order = Order(
        user_id=current_user.id,
        total_amount=final_amount,
        points_redeemed=points_redeemed_count,
        status='Placed'
    )
    db.session.add(new_order)
    db.session.flush() 
    
    for item, qty in items_to_process:
        order_item = OrderItem(
            order_id=new_order.id,
            item_id=item.id,
            quantity=qty,
            unit_price=item.price
        )
        db.session.add(order_item)
        
    # Earn new points on final paid amount (1 point per KSh 10)[cite: 1]
    points_earned = int(final_amount // 10)
    if points_earned > 0:
        current_user.points_balance = (current_user.points_balance or 0) + points_earned
        loyalty_tx = LoyaltyTransaction(
            user_id=current_user.id,
            order_id=new_order.id,
            transaction_type='Credit',
            points=points_earned
        )
        db.session.add(loyalty_tx)
        
    db.session.commit()
    session.pop('cart', None)
    flash(f'Order placed successfully! Earned {points_earned} points!', 'success')
    return redirect(url_for('student.menu'))

@student_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('student/dashboard.html', user=current_user)