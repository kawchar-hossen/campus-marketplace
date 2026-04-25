from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user

from app import db
from app.models.order import Order
from app.models.product import Product

order = Blueprint("order", __name__)


# Buy Product
@order.route("/buy/<int:product_id>")
@login_required
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.seller_id == current_user.id:
        flash("You cannot buy your own product.", "danger")
        return redirect(url_for("product.product_detail", id=product.id))

    existing = Order.query.filter_by(
        buyer_id=current_user.id,
        product_id=product.id
    ).first()

    if existing:
        flash("You already ordered this product.", "warning")
        return redirect(url_for("product.product_detail", id=product.id))

    new_order = Order(
        buyer_id=current_user.id,
        product_id=product.id,
        status="Pending"
    )

    db.session.add(new_order)
    db.session.commit()

    flash("Order placed successfully.", "success")
    return redirect(url_for("order.my_orders"))


# Buyer Orders
@order.route("/orders")
@login_required
def my_orders():
    orders = Order.query.filter_by(
        buyer_id=current_user.id
    ).order_by(Order.ordered_at.desc()).all()

    return render_template("orders.html", orders=orders)


# Seller Dashboard
@order.route("/seller/orders")
@login_required
def seller_orders():
    sales = Order.query.join(Product).filter(
        Product.seller_id == current_user.id
    ).order_by(Order.ordered_at.desc()).all()

    return render_template("seller_orders.html", sales=sales)


# Update Status
@order.route("/order/complete/<int:id>")
@login_required
def complete_order(id):
    item = Order.query.get_or_404(id)

    if item.product.seller_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect("/")

    item.status = "Completed"
    db.session.commit()

    flash("Order marked completed.", "success")
    return redirect(url_for("order.seller_orders"))