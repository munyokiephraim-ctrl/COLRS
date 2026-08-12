from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user

from app import db
from app.models import MenuItem, Order, OrderItem, LoyaltyTransaction

student_bp = Blueprint("student", __name__)

POINTS_REDEMPTION_RATE = 1   # 1 point = KSh 1 off
MIN_REDEEM_POINTS = 50


# ==========================
# Student Protection
# ==========================

@student_bp.before_request
@login_required
def require_student():
    if current_user.role.lower() != "student":
        return redirect(url_for("admin.dashboard"))


# ==========================
# Dashboard
# ==========================

@student_bp.route("/dashboard")
def dashboard():

    orders = (
        Order.query
        .filter_by(user_id=current_user.id)
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

    key = str(item.id)

    if key in cart:
        cart[key] += 1
    else:
        cart[key] = 1

    session["cart"] = cart
    session.modified = True

    flash(f"{item.name} added to cart!", "success")

    return redirect(url_for("student.view_cart"))

# ==========================
# Increase Cart Quantity
# ==========================

@student_bp.route("/cart/increase/<int:item_id>", methods=["POST"])
def increase_cart(item_id):

    cart = session.get("cart", {})

    key = str(item_id)

    if key in cart:
        cart[key] += 1

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("student.view_cart"))


# ==========================
# Decrease Cart Quantity
# ==========================

@student_bp.route("/cart/decrease/<int:item_id>", methods=["POST"])
def decrease_cart(item_id):

    cart = session.get("cart", {})

    key = str(item_id)

    if key in cart:

        cart[key] -= 1

        if cart[key] <= 0:
            cart.pop(key)

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("student.view_cart"))


# ==========================
# View Cart
# ==========================

@student_bp.route("/cart")
@student_bp.route("/view-cart", endpoint="view_cart")
def cart():

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

@student_bp.route("/checkout", methods=["GET", "POST"])
def checkout():

    cart = session.get("cart", {})

    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("student.view_cart"))

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

    # -----------------------
    # Show Checkout Page
    # -----------------------

    if request.method == "GET":
        max_redeemable = min(current_user.points_balance, int(subtotal))
        return render_template(
            "student/checkout.html",
            cart_items=cart_items,
            subtotal=subtotal,
            points_balance=current_user.points_balance,
            min_redeem_points=MIN_REDEEM_POINTS,
            max_redeemable=max_redeemable
    )

    # -----------------------
    # Complete Order
    # -----------------------

    payment_method = request.form.get("payment_method")
    phone = request.form.get("phone")
    redeem_points = request.form.get("redeem_points") == "on"

    points_to_debit = 0
    if redeem_points and current_user.points_balance >= MIN_REDEEM_POINTS:
        points_to_debit = min(current_user.points_balance, int(subtotal))

    order = Order(
        user_id=current_user.id,
        total_amount=0,
        points_redeemed=points_to_debit,
        status="Placed"
    )
    db.session.add(order)
    db.session.commit()

    for item in cart_items:
        db.session.add(
            OrderItem(
                order_id=order.id,
                item_id=item["item"].id,
                quantity=item["quantity"],
                unit_price=item["item"].price
            )
        )

    final_total = subtotal - points_to_debit
    order.total_amount = final_total

    earned_points = int(final_total * 0.10)
    current_user.points_balance += earned_points

    db.session.add(
        LoyaltyTransaction(
            user_id=current_user.id,
            order_id=order.id,
            transaction_type="Credit",
            points=earned_points
        )
    )

    if points_to_debit > 0:
        current_user.points_balance -= points_to_debit
        db.session.add(
            LoyaltyTransaction(
                user_id=current_user.id,
                order_id=order.id,
                transaction_type="Debit",
                points=points_to_debit
            )
        )

    db.session.commit()
    session.pop("cart", None)

    flash(
        f"Order placed via {payment_method}! Earned {earned_points} pts"
        + (f", redeemed {points_to_debit} pts (KSh {points_to_debit} off)." if points_to_debit else "."),
        "success"
    )

    return redirect(url_for("student.dashboard"))

# ==========================
# Order Details
# ==========================

@student_bp.route("/order/<int:order_id>")
def order_details(order_id):

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "student/order_details.html",
        order=order
    )