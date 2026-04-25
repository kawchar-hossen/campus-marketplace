from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user

from app import db
from app.models.wishlist import Wishlist
from app.models.product import Product

wishlist = Blueprint("wishlist", __name__)


# Add Wishlist
@wishlist.route("/wishlist/add/<int:product_id>")
@login_required
def add_wishlist(product_id):
    existing = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if not existing:
        item = Wishlist(
            user_id=current_user.id,
            product_id=product_id
        )
        db.session.add(item)
        db.session.commit()
        flash("Added to wishlist.", "success")

    return redirect(url_for("product.all_products"))


# Remove Wishlist
@wishlist.route("/wishlist/remove/<int:id>")
@login_required
def remove_wishlist(id):
    item = Wishlist.query.get_or_404(id)

    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash("Removed from wishlist.", "info")

    return redirect(url_for("wishlist.my_wishlist"))


# My Wishlist
@wishlist.route("/wishlist")
@login_required
def my_wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template("wishlist.html", items=items)