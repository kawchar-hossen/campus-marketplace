from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user

# import service functions
from app.services.order_service import (
    place_order,
    get_user_orders,
    get_seller_orders,
    complete_order
)

# import model + db (for cancel)
from app.models import Order
from app import db

order = Blueprint("order", __name__)


# ✅ Buy Product
@order.route("/buy/<int:product_id>")
@login_required
def buy_product(product_id):
    new_order, error = place_order(current_user, product_id)

    if error:
        flash(error, "danger")
        return redirect(url_for("product.product_detail", id=product_id))

    flash("Order placed successfully.", "success")
    return redirect(url_for("order.my_orders"))


# ✅ Buyer Orders
@order.route("/orders")
@login_required
def my_orders():
    orders = get_user_orders(current_user)
    return render_template("orders.html", orders=orders)


# ✅ Seller Orders Dashboard
@order.route("/seller/orders")
@login_required
def seller_orders():
    sales = get_seller_orders(current_user)
    return render_template("seller_orders.html", sales=sales)


# ✅ Mark Order Completed
@order.route("/order/complete/<int:id>")
@login_required
def complete(id):
    error = complete_order(current_user, id)

    if error:
        flash(error, "danger")
        return redirect("/")

    flash("Order marked completed.", "success")
    return redirect(url_for("order.seller_orders"))


# ✅ Cancel Order (NEW)
@order.route("/cancel/<int:order_id>", methods=["POST"])
@login_required
def cancel_order(order_id):
    order_item = Order.query.get_or_404(order_id)

    # 🔐 Security check
    if order_item.buyer_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for("order.my_orders"))

    # ❌ Only pending orders can be cancelled
    if order_item.status != "Pending":
        flash("Order cannot be cancelled!", "warning")
        return redirect(url_for("order.my_orders"))

    # 🔄 Update status
    order_item.status = "Cancelled"
    db.session.commit()

    flash("Order cancelled successfully!", "success")
    return redirect(url_for("order.my_orders"))