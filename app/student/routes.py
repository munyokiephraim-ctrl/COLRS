from flask import Blueprint, request, redirect, url_for, session, flash, render_template  # Add render_template here!
from flask_login import login_required, current_user
from app import db
from app.models import MenuItem, Order, OrderItem, Restaurant, LoyaltyTransaction

student_bp = Blueprint('student', __name__)

@student_bp.route('/menu')
@login_required
def menu():
    available_items = MenuItem.query.all()
    return render_template('student/menu.html', items=available_items, user=current_user)

    # Handle order placement
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        quantity = request.form.get('quantity', 1, type=int)
        
        item = MenuItem.query.get(item_id)
        if item:
            total_cost = item.price * quantity
            new_order = Order(user_id=current_user.id, total_amount=total_cost, status='Placed')
            db.session.add(new_order)
            db.session.commit()
            
            order_item = OrderItem(order_id=new_order.id, item_id=item.id, quantity=quantity, unit_price=item.price)
            db.session.add(order_item)
            db.session.commit()
            
            return f"Order Placed Successfully! <a href='/menu'>Back to Menu</a>"

    # Fetch available items and send them to the HTML template
    available_items = MenuItem.query.all()
    return render_template('menu.html', items=available_items)

@student_bp.route('/restaurants')
def browse_restaurants():
    # Query all restaurants from the database
    restaurants = Restaurant.query.all()
    # Pass them to the template
    return render_template('student/restaurants.html', restaurants=restaurants)

@student_bp.route('/cart/add/<int:item_id>')
@login_required
def add_to_cart(item_id):
    # Initialize cart session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    item_id_str = str(item_id)
    
    # Add item or increment quantity
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
        
    # Calculate total amount
    total_amount = 0
    items_to_process = []
    for item_id, qty in cart.items():
        item = MenuItem.query.get(int(item_id))
        if item:
            total_amount += item.price * qty
            items_to_process.append((item, qty))

    # 1. Create Main Order Record
    new_order = Order(
        user_id=current_user.user_id,
        total_amount=total_amount,
        points_redeemed=0,
        status='Placed'
    )
    db.session.add(new_order)
    db.session.flush()  # Generates the order_id before committing
    
    # 2. Create OrderItem Line Records
    for item, qty in items_to_process:
        order_item = OrderItem(
            order_id=new_order.order_id,
            item_id=item.item_id,
            quantity=qty,
            unit_price=item.price
        )
        db.session.add(order_item)
        
    # 3. Calculate and Award Loyalty Points (1 point per 10 KSh)
    points_earned = int(total_amount // 10)
    if points_earned > 0:
        current_user.points_balance = (current_user.points_balance or 0) + points_earned
        
        loyalty_tx = LoyaltyTransaction(
            user_id=current_user.user_id,
            order_id=new_order.order_id,
            transaction_type='Credit',
            points=points_earned
        )
        db.session.add(loyalty_tx)
        
    # Commit transaction, clear cart session cache
    db.session.commit()
    session.pop('cart', None)
    
    flash(u'Order placed successfully! Earned {} points!'.format(points_earned), 'success')
    return redirect(url_for('student.menu'))        
    
@student_bp.route('/dashboard')
@login_required
def dashboard():
    # This renders the dashboard and passes the logged-in user's info
    return render_template('student/dashboard.html', user=current_user)
    # Generate the menu catalog interface dynamically
    menu_html = ""
    for item in available_items:
        menu_html += f'''
            <div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                <h4>{item.name} <span style="color: green;">- KSh {item.price:.2f}</span></h4>
                <p style="color: #555; font-size: 0.9em;">{item.description if item.description else "No description provided."}</p>
                <form method="POST" style="display: inline;">
                    <input type="hidden" name="item_id" value="{item.id}">
                    <label>Qty:</label>
                    <input type="number" name="quantity" value="1" min="1" style="width: 40px;">
                    <button type="submit">Place Order</button>
                </form>
            </div>
        '''

    return f'''
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f7f9fc; color: #2d3748; margin: 0; padding: 0; display: flex; justify-content: center; }}
            .mobile-screen {{ max-width: 480px; width: 100%; min-height: 100vh; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.05); padding: 25px; box-sizing: border-box; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #edf2f7; padding-bottom: 15px; margin-bottom: 20px; }}
            h2 {{ color: #dd6b20; margin: 0; font-size: 1.6rem; letter-spacing: 1px; }}
            .logout-btn {{ color: #e53e3e; text-decoration: none; font-size: 0.9rem; font-weight: bold; border: 1px solid #fed7d7; padding: 6px 12px; border-radius: 6px; background: #fff5f5; }}
            .logout-btn:hover {{ background: #fed7d7; }}
            .balance-card {{ background: linear-gradient(135deg, #ed8936, #dd6b20); color: white; padding: 20px; border-radius: 16px; margin-bottom: 25px; box-shadow: 0 4px 14px rgba(221, 107, 32, 0.25); }}
            .balance-card h3 {{ margin: 0; font-size: 0.85rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; }}
            .balance-card .amount {{ font-size: 2rem; font-weight: bold; margin-top: 5px; }}
            .menu-item {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px; margin-bottom: 18px; box-shadow: 0 4px 6px rgba(0,0,0,0.01); display: flex; flex-direction: column; }}
            .menu-item-header {{ display: flex; justify-content: space-between; align-items: baseline; }}
            .menu-item-title {{ font-size: 1.15rem; font-weight: bold; color: #2d3748; margin: 0; }}
            .menu-item-price {{ font-size: 1.15rem; font-weight: bold; color: #38a169; }}
            .menu-item-desc {{ color: #718096; font-size: 0.9rem; margin: 8px 0 15px 0; line-height: 1.4; }}
            .order-form {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; border-top: 1px dashed #e2e8f0; padding-top: 14px; }}
            .qty-selector {{ display: flex; align-items: center; gap: 8px; font-size: 0.9rem; font-weight: 600; color: #4a5568; }}
            input[type="number"] {{ width: 55px; padding: 8px; border: 1px solid #cbd5e0; border-radius: 8px; text-align: center; font-size: 0.95rem; font-weight: bold; }}
            .order-btn {{ background: #dd6b20; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 0.95rem; flex-grow: 1; transition: background 0.2s; }}
            .order-btn:hover {{ background: #c05621; }}
        </style>

        <div class="mobile-screen">
            <div class="header">
                <h2>COLRS</h2>
                <a href="/auth/logout" class="logout-btn">Logout</a>
            </div>
            
            <div class="balance-card">
                <h3>Loyalty Wallet</h3>
                <div class="amount">🪙 {current_user.points_balance} Points</div>
                <div style="font-size: 0.85rem; margin-top: 8px; opacity: 0.9;">Welcome back, <strong>{current_user.full_name}</strong></div>
            </div>
            
            <h3 style="color: #2d3748; margin-bottom: 15px; font-size: 1.2rem;">Available Meals Today</h3>
            <div>
                {menu_html if menu_html else "<p style='color: #a0aec0; text-align: center; margin-top: 40px;'>The kitchen hasn't uploaded any items yet.</p>"}
            </div>
        </div>
    '''