# app/routes/order_routes.py

from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user

from app import db
from app.models import Order

# services
from app.services.order_service import (
    place_order,
    get_user_orders,
    get_seller_orders,
    complete_order
)

order = Blueprint("order", __name__)


# =====================================
# BUY PRODUCT
# =====================================
@order.route("/buy/<int:product_id>")
@login_required
def buy_product(product_id):
    new_order, error = place_order(current_user, product_id)

    if error:
        flash(error, "danger")
        return redirect(url_for("product.product_detail", id=product_id))

    flash("Order placed successfully.", "success")
    return redirect(url_for("order.my_orders"))


# =====================================
# BUYER ORDERS
# =====================================
@order.route("/orders")
@login_required
def my_orders():
    orders = get_user_orders(current_user)
    return render_template("orders.html", orders=orders)


# =====================================
# SELLER ORDERS
# =====================================
@order.route("/seller/orders")
@login_required
def seller_orders():
    sales = get_seller_orders(current_user)
    return render_template("seller_orders.html", sales=sales)


# =====================================
# COMPLETE ORDER
# =====================================
@order.route("/order/complete/<int:id>")
@login_required
def complete(id):
    error = complete_order(current_user, id)

    if error:
        flash(error, "danger")
        return redirect(url_for("order.seller_orders"))

    flash("Order marked completed.", "success")
    return redirect(url_for("order.seller_orders"))


# =====================================
# CANCEL ORDER
# =====================================
@order.route("/cancel/<int:order_id>", methods=["POST"])
@login_required
def cancel_order(order_id):
    order_item = Order.query.get_or_404(order_id)

    # Security check
    if order_item.buyer_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for("order.my_orders"))

    # Only pending order can cancel
    if order_item.status != "Pending":
        flash("Only pending orders can be cancelled.", "warning")
        return redirect(url_for("order.my_orders"))

    order_item.status = "Cancelled"
    db.session.commit()

    flash("Order cancelled successfully!", "success")
    return redirect(url_for("order.my_orders"))


# =====================================
# DELETE ORDER (ONLY CANCELLED)
# =====================================
@order.route("/delete/<int:order_id>", methods=["POST"])
@login_required
def delete_order(order_id):
    order_item = Order.query.get_or_404(order_id)

    # Security check
    if order_item.buyer_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for("order.my_orders"))

    # Only cancelled order can delete
    if order_item.status != "Cancelled":
        flash("Only cancelled orders can be deleted.", "warning")
        return redirect(url_for("order.my_orders"))

    db.session.delete(order_item)
    db.session.commit()

    flash("Order deleted successfully!", "success")
    return redirect(url_for("order.my_orders"))