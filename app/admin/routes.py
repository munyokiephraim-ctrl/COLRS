from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Order

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Query all orders, sorting by most recent first
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/dashboard.html', orders=all_orders, user=current_user)

@admin_bp.route('/order/<int:order_id>/update/<string:new_status>', methods=['POST'])
@login_required
def update_order_status(order_id, new_status):
    order = Order.query.get_or_404(order_id)
    if new_status in ['Placed', 'Preparing', 'Ready']:
        order.status = new_status
        db.session.commit()
        flash('Order #{} status updated to {}!'.format(order_id, new_status), 'success')
    return redirect(url_for('admin.dashboard'))