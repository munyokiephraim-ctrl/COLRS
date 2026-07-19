from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import MenuItem, Order

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def require_admin():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('student.menu'))

@admin_bp.route('/dashboard')
def dashboard():
    active_orders = Order.query.filter(Order.status != 'Completed').order_by(Order.created_at.desc()).all()
    return render_template('admin/dashboard.html', orders=active_orders)

@admin_bp.route('/menu', methods=['GET', 'POST'])
def manage_menu():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        
        new_item = MenuItem(
            name=name,
            description=description,
            price=price,
            category=category,
            is_available=True
        )
        db.session.add(new_item)
        db.session.commit()
        
        flash(f'Menu item "{name}" added successfully!', 'success')
        return redirect(url_for('admin.manage_menu'))
        
    items = MenuItem.query.all()
    return render_template('admin/menu_manager.html', items=items)

@admin_bp.route('/order/<int:order_id>/update', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['Placed', 'Preparing', 'Ready', 'Completed']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}.', 'success')
        
    return redirect(url_for('admin.dashboard'))