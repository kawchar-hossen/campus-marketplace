from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.order import Order
from app.models.user import User

payment = Blueprint("payment", __name__)


# =========================
# PAYMENT PAGE + SUBMIT PAYMENT
# =========================
@payment.route("/payment/<int:order_id>", methods=["GET", "POST"])
@login_required
def payment_page(order_id):

    order = Order.query.get_or_404(order_id)
    seller = User.query.get(order.seller_id)

    # =========================
    # POST = SUBMIT PAYMENT
    # =========================
    if request.method == "POST":

        trxid = request.form.get("trxid")
        sender_number = request.form.get("sender_number")

        # validation
        if not trxid:
            flash("Transaction ID is required", "danger")
            return redirect(url_for("payment.payment_page", order_id=order.id))

        if not sender_number:
            flash("Sender number required", "danger")
            return redirect(url_for("payment.payment_page", order_id=order.id))

        # save payment info in order
        order.trxid = trxid
        order.status = "waiting_verification"

        db.session.commit()

        flash("Payment submitted successfully!", "success")
        return redirect(url_for("order.my_orders"))

    # =========================
    # GET = SHOW PAGE
    # =========================
    return render_template(
        "payment.html",
        order=order,
        seller=seller
    )