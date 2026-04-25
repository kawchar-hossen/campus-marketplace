from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user

from app import db
from app.models.wishlist import Wishlist
from app.models.product import Product

wishlist = Blueprint("wishlist", __name__)


# ==========================
# Add to Wishlist
# ==========================
@wishlist.route("/wishlist/add/<int:product_id>")
@login_required
def add_wishlist(product_id):

    print("Wishlist route hit:", product_id)

    # Check product exists
    product = Product.query.get_or_404(product_id)

    # Prevent duplicate wishlist item
    existing = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product.id
    ).first()

    if existing:
        print("Already exists in wishlist")
        flash("Already added in wishlist.", "warning")

    else:
        new_item = Wishlist(
            user_id=current_user.id,
            product_id=product.id
        )

        db.session.add(new_item)
        db.session.commit()

        print("Inserted successfully")
        flash("Product added to wishlist.", "success")

    return redirect(url_for("product.all_products"))


# ==========================
# Remove Wishlist Item
# ==========================
@wishlist.route("/wishlist/remove/<int:id>")
@login_required
def remove_wishlist(id):

    item = Wishlist.query.get_or_404(id)

    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()

        print("Wishlist item removed:", id)
        flash("Removed from wishlist.", "info")

    else:
        print("Unauthorized remove attempt:", id)
        flash("Unauthorized action.", "danger")

    return redirect(url_for("wishlist.my_wishlist"))


# ==========================
# My Wishlist
# ==========================
@wishlist.route("/wishlist")
@login_required
def my_wishlist():

    items = Wishlist.query.filter_by(
        user_id=current_user.id
    ).all()

    valid_items = []

    for item in items:
        if item.product:
            valid_items.append(item)
        else:
            print("Deleted broken wishlist row:", item.id)
            db.session.delete(item)

    db.session.commit()

    print("Wishlist loaded. Total items:", len(valid_items))

    return render_template(
        "wishlist.html",
        items=valid_items
    )