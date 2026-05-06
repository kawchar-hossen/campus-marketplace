from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.order import Order
from app.models.product import Product

order = Blueprint("order", __name__)


# =====================================
# 🛒 BUY PRODUCT → CREATE ORDER
# =====================================
@order.route("/buy/<int:product_id>", methods=["GET", "POST"])
@login_required
def buy(product_id):

    product = Product.query.get_or_404(product_id)

    # ❗ prevent self purchase
    if product.seller_id == current_user.id:
        flash("You cannot buy your own product", "danger")
        return redirect(url_for("product.all_products"))

    if request.method == "POST":

        payment_method = request.form.get("payment_method")

        if not payment_method:
            flash("Please select payment method", "warning")
            return redirect(url_for("order.buy", product_id=product_id))

        # CREATE ORDER
        new_order = Order(
            buyer_id=current_user.id,
            seller_id=product.seller_id,
            product_id=product.id,
            payment_method=payment_method
        )

        # STATUS LOGIC
        if payment_method == "cod":
            new_order.status = "pending"

        elif payment_method in ["bkash", "nagad"]:
            new_order.status = "waiting_verification"

        else:
            flash("Invalid payment method", "danger")
            return redirect(url_for("order.buy", product_id=product_id))

        db.session.add(new_order)
        db.session.commit()

        # REDIRECT
        if payment_method in ["bkash", "nagad"]:
            return redirect(url_for("payment.payment_page", order_id=new_order.id))

        flash("Order placed successfully (Cash on Delivery)", "success")
        return redirect(url_for("order.my_orders"))

    return render_template("buy.html", product=product)


# =====================================
# 📦 BUYER ORDERS
# =====================================
@order.route("/orders")
@login_required
def my_orders():

    orders = Order.query.filter_by(
        buyer_id=current_user.id
    ).order_by(Order.id.desc()).all()

    return render_template("orders.html", orders=orders)


# =====================================
# 🧾 CANCEL ORDER
# =====================================
@order.route("/cancel/<int:order_id>")
@login_required
def cancel_order(order_id):

    order_obj = Order.query.get_or_404(order_id)

    if order_obj.buyer_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("order.my_orders"))

    if order_obj.status == "paid":
        flash("Cannot cancel paid order", "danger")
        return redirect(url_for("order.my_orders"))

    order_obj.status = "cancelled"
    db.session.commit()

    flash("Order cancelled", "success")
    return redirect(url_for("order.my_orders"))


# =====================================
# 🏪 SELLER ORDERS
# =====================================
@order.route("/seller/orders")
@login_required
def seller_orders():

    orders = Order.query.filter_by(
        seller_id=current_user.id
    ).order_by(Order.id.desc()).all()

    return render_template("seller_orders.html", orders=orders)


# =====================================
# ✅ SELLER CONFIRM PAYMENT (NEW)
# =====================================
@order.route("/confirm-payment/<int:order_id>")
@login_required
def confirm_payment(order_id):

    order_obj = Order.query.get_or_404(order_id)

    # only seller can confirm
    if order_obj.seller_id != current_user.id:
        flash("You are not allowed to confirm this payment", "danger")
        return redirect(url_for("order.seller_orders"))

    # only pending verification orders
    if order_obj.status != "waiting_verification":
        flash("This order cannot be confirmed", "warning")
        return redirect(url_for("order.seller_orders"))

    order_obj.status = "paid"
    db.session.commit()

    flash("Payment confirmed successfully!", "success")
    return redirect(url_for("order.seller_orders"))