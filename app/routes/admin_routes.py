from flask import Blueprint, render_template, redirect, flash
from flask_login import login_required, current_user

from app import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order

admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required():
    return current_user.is_authenticated and current_user.is_admin


# Dashboard
@admin.route("/")
@login_required
def dashboard():
    if not admin_required():
        return redirect("/")

    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()

    users = User.query.all()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        users=users
    )


# Ban User
@admin.route("/ban/<int:id>")
@login_required
def ban_user(id):
    if not admin_required():
        return redirect("/")

    user = User.query.get_or_404(id)
    user.is_banned = True
    db.session.commit()

    flash("User banned.", "warning")
    return redirect("/admin/")


# Unban User
@admin.route("/unban/<int:id>")
@login_required
def unban_user(id):
    if not admin_required():
        return redirect("/")

    user = User.query.get_or_404(id)
    user.is_banned = False
    db.session.commit()

    flash("User unbanned.", "success")
    return redirect("/admin/")


# Delete Product
@admin.route("/delete-product/<int:id>")
@login_required
def delete_product(id):
    if not admin_required():
        return redirect("/")

    product = Product.query.get_or_404(id)

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted.", "danger")
    return redirect("/admin/")