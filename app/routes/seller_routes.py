from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.order import Order

seller = Blueprint("seller", __name__)


# =====================================
# SELLER ORDERS DASHBOARD
# =====================================
@seller.route("/seller/orders")
@login_required
def seller_orders():

    orders = (
        Order.query
        .filter_by(seller_id=current_user.id)
        .order_by(Order.id.desc())
        .all()
    )

    return render_template("seller_orders.html", orders=orders)


# =====================================
# VERIFY PAYMENT (APPROVE / REJECT)
# =====================================
@seller.route("/verify/<int:order_id>", methods=["POST"])
@login_required
def verify(order_id):

    order = Order.query.get_or_404(order_id)

    # ❗ SECURITY CHECK: only seller can verify
    if order.seller_id != current_user.id:
        flash("Unauthorized action", "danger")
        return redirect(url_for("seller.seller_orders"))

    action = request.form.get("action")

    # =========================
    # APPROVE PAYMENT
    # =========================
    if action == "approve":
        order.status = "paid"

    # =========================
    # REJECT PAYMENT
    # =========================
    elif action == "reject":
        order.status = "payment_failed"
        order.trxid = None

    else:
        flash("Invalid action", "warning")
        return redirect(url_for("seller.seller_orders"))

    db.session.commit()

    flash("Order updated successfully", "success")
    return redirect(url_for("seller.seller_orders"))