from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models import MenuItem, Order, User

admin_bp = Blueprint("admin", __name__)


# ==================================================
# ADMIN PROTECTION
# ==================================================

@admin_bp.before_request
@login_required
def require_admin():

    if current_user.role.lower() != "admin":
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for("student.menu"))


# ==================================================
# DASHBOARD
# ==================================================

@admin_bp.route("/dashboard")
def dashboard():

    orders = (
        Order.query
        .order_by(Order.created_at.desc())
        .all()
    )

    return render_template(
        "admin/dashboard.html",

        orders=orders,

        recent_orders=orders[:10],

        total_orders=Order.query.count(),

        total_meals=MenuItem.query.count(),

        total_students=User.query.filter_by(role="student").count(),

        pending_orders=Order.query.filter_by(status="Placed").count()
    )


# ==================================================
# UPDATE ORDER STATUS
# ==================================================

@admin_bp.route("/order/<int:order_id>/update", methods=["POST"])
def update_order_status(order_id):

    order = Order.query.get_or_404(order_id)

    new_status = request.form.get("status")

    if new_status in [
        "Placed",
        "Preparing",
        "Ready",
        "Completed"
    ]:

        order.status = new_status

        db.session.commit()

        flash(
            f"Order #{order.id} updated successfully.",
            "success"
        )

    return redirect(url_for("admin.dashboard"))


# ==================================================
# MENU MANAGER
# ==================================================

@admin_bp.route("/menu")
def manage_menu():

    items = (
        MenuItem.query
        .order_by(MenuItem.category, MenuItem.name)
        .all()
    )

    return render_template(
        "admin/menu_manager.html",
        items=items
    )


# ==================================================
# ADD MENU ITEM
# ==================================================

@admin_bp.route("/menu/add", methods=["GET", "POST"])
def add_menu_item():

    if request.method == "POST":

        item = MenuItem(
            name=request.form.get("name"),
            description=request.form.get("description"),
            price=float(request.form.get("price")),
            category=request.form.get("category"),
            is_available=True
        )

        db.session.add(item)
        db.session.commit()

        flash(
            "Menu item added successfully!",
            "success"
        )

        return redirect(url_for("admin.manage_menu"))

    return render_template(
        "admin/add_menu_item.html"
    )


# ==================================================
# EDIT MENU ITEM
# ==================================================

@admin_bp.route("/menu/edit/<int:item_id>", methods=["GET", "POST"])
def edit_menu_item(item_id):

    item = MenuItem.query.get_or_404(item_id)

    if request.method == "POST":

        item.name = request.form.get("name")
        item.description = request.form.get("description")
        item.price = float(request.form.get("price"))
        item.category = request.form.get("category")

        item.is_available = (
            request.form.get("is_available") == "on"
        )

        db.session.commit()

        flash(
            "Menu item updated successfully!",
            "success"
        )

        return redirect(url_for("admin.manage_menu"))

    return render_template(
        "admin/edit_menu_item.html",
        item=item
    )


# ==================================================
# DELETE MENU ITEM
# ==================================================

@admin_bp.route("/menu/delete/<int:item_id>", methods=["POST"])
def delete_menu_item(item_id):

    item = MenuItem.query.get_or_404(item_id)

    db.session.delete(item)
    db.session.commit()

    flash(
        "Menu item deleted successfully.",
        "success"
    )

    return redirect(url_for("admin.manage_menu"))