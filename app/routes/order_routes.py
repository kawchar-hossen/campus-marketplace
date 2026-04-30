from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.order import Order

# =========================
# BLUEPRINT
# =========================
order = Blueprint("order", __name__)


# =========================
# BUY ROUTE → PAYMENT FIRST
# =========================
@order.route("/buy/<int:product_id>")
@login_required
def buy_redirect(product_id):

    # 👉 Redirect to payment system
    return redirect(url_for("payment.payment_page", product_id=product_id))