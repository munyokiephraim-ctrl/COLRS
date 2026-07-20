from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user

from app import db
from app.models import MenuItem, Order, OrderItem, LoyaltyTransaction

student_bp = Blueprint("student", __name__)


@student_bp.before_request
@login_required
def require_student():
    if current_user.role != "student":
        return redirect(url_for("admin.dashboard"))


# ==========================
# Dashboard
# ==========================
@student_bp.route("/dashboard")
def dashboard():
    orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return render_template(
        "student/dashboard.html",
        orders=orders
    )


# ==========================
# Menu
# ==========================
@student_bp.route("/menu")
def menu():

    category = request.args.get("category", "All")

    if category == "All":
        items = MenuItem.query.filter_by(is_available=True).all()
    else:
        items = MenuItem.query.filter_by(
            category=category,
            is_available=True
        ).all()

    categories = (
        db.session.query(MenuItem.category)
        .distinct()
        .all()
    )

    categories = [c[0] for c in categories]

    return render_template(
        "student/menu.html",
        items=items,
        categories=categories,
        active_category=category
    )


# ==========================
# Add To Cart
# ==========================
@student_bp.route("/cart/add/<int:item_id>", methods=["POST"])
def add_to_cart(item_id):
    item = MenuItem.query.get_or_404(item_id)

    cart = session.get("cart", {})

    item_key = str(item.id)

    if item_key in cart:
        cart[item_key] += 1
    else:
        cart[item_key] = 1

    session["cart"] = cart
    session.modified = True

    print("AFTER ADD:", dict(session))

    flash(f"{item.name} added to cart!", "success")

    return redirect(url_for("student.view_cart"))

# ==========================
# Cart
# ==========================
@student_bp.route("/cart")
@student_bp.route("/view-cart", endpoint="view_cart")
def cart():

    print("INSIDE CART:", dict(session))

    cart = session.get("cart", {})

    cart_items = []
    subtotal = 0

    for item_id, qty in cart.items():
        item = MenuItem.query.get(int(item_id))

        if item:
            total = item.price * qty
            subtotal += total

            cart_items.append({
                "item": item,
                "quantity": qty,
                "total": total
            })

    return render_template(
        "student/cart.html",
        cart_items=cart_items,
        subtotal=subtotal
    )

# ==========================
# Checkout
# ==========================
@student_bp.route("/checkout", methods=["POST"])
def checkout():

    cart = session.get("cart", {})

    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("student.view_cart"))

    subtotal = 0

    order = Order(
        user_id=current_user.id,
        total_amount=0,
        status="Placed"
    )

    db.session.add(order)
    db.session.commit()

    for item_id, qty in cart.items():

        item = MenuItem.query.get(int(item_id))

        if item:

            subtotal += item.price * qty

            db.session.add(
                OrderItem(
                    order_id=order.id,
                    item_id=item.id,
                    quantity=qty,
                    unit_price=item.price
                )
            )

    order.total_amount = subtotal

    earned_points = int(subtotal * 0.1)

    current_user.points_balance += earned_points

    db.session.add(
        LoyaltyTransaction(
            user_id=current_user.id,
            order_id=order.id,
            transaction_type="Credit",
            points=earned_points
        )
    )

    db.session.commit()

    session.pop("cart", None)

    flash(
        f"Order placed successfully! You earned {earned_points} points.",
        "success",
    )

    return redirect(url_for("student.dashboard"))