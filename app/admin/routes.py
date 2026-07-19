from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Order, MenuItem

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('student.menu'))
        
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/dashboard.html', orders=all_orders, user=current_user)

@admin_bp.route('/order/<int:order_id>/update/<string:new_status>', methods=['POST'])
@login_required
def update_order_status(order_id, new_status):
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('student.menu'))

    order = Order.query.get_or_404(order_id)
    if new_status in ['Placed', 'Preparing', 'Ready']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}.', 'success')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/menu', methods=['GET', 'POST'])
@login_required
def menu_manager():
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('student.menu'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        
        if not name or not price or not category:
            flash("Name, price, and category are required.", "danger")
        else:
            try:
                new_item = MenuItem(
                    name=name,
                    description=description,
                    price=float(price),
                    category=category
                )
                db.session.add(new_item)
                db.session.commit()
                flash('Menu item added successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding item: {str(e)}', 'danger')
        return redirect(url_for('admin.menu_manager'))

    items = MenuItem.query.all()
    return render_template('admin/menu_manager.html', items=items, user=current_user)

@admin_bp.route('/menu/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_menu_item(item_id):
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('student.menu'))
    
    item = MenuItem.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Menu item deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete item because it is tied to past orders.', 'danger')
        
    return redirect(url_for('admin.menu_manager'))