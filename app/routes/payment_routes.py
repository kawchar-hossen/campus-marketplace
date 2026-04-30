from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user

from app import db
from app.models.product import Product
from app.models.order import Order
from app.services.bkash_service import generate_bkash_otp, verify_bkash_otp

payment = Blueprint("payment", __name__)


# =========================
# START PAYMENT (CLICK BUY)
# =========================
@payment.route("/payment/<int:product_id>")
@login_required
def payment_page(product_id):

    product = Product.query.get_or_404(product_id)

    session["pending_product_id"] = product_id

    return render_template("payment.html", product=product)


# =========================
# SEND OTP (Bkash simulation)
# =========================
@payment.route("/payment/send-otp", methods=["POST"])
@login_required
def send_otp():

    phone = current_user.phone

    otp = generate_bkash_otp(phone)

    flash(f"OTP sent to your phone: {otp}", "info")  # simulate SMS

    return redirect(url_for("payment.verify_payment"))


# =========================
# VERIFY PAYMENT
# =========================
@payment.route("/payment/verify", methods=["GET", "POST"])
@login_required
def verify_payment():

    product_id = session.get("pending_product_id")

    if not product_id:
        flash("Session expired", "danger")
        return redirect(url_for("main.home"))

    product = Product.query.get_or_404(product_id)

    if request.method == "POST":

        otp = request.form.get("otp")

        phone = current_user.phone

        if verify_bkash_otp(phone, otp):

            # CREATE ORDER AFTER PAYMENT SUCCESS
            order = Order(
                buyer_id=current_user.id,
                product_id=product.id,
                status="Paid"
            )

            db.session.add(order)
            db.session.commit()

            session.pop("pending_product_id", None)

            flash("Payment successful & order placed!", "success")
            return redirect(url_for("order.my_orders"))

        else:
            flash("Invalid OTP", "danger")

    return render_template("verify_payment.html", product=product)