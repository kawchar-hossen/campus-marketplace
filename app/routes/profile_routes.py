from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.seller_profile import SellerProfile

profile = Blueprint("profile", __name__)


# =====================================
# CREATE / UPDATE SELLER PROFILE
# =====================================
@profile.route("/seller/profile", methods=["GET", "POST"])
@login_required
def seller_profile():

    profile = SellerProfile.query.filter_by(user_id=current_user.id).first()

    # create if not exists
    if not profile:
        profile = SellerProfile(user_id=current_user.id)
        db.session.add(profile)

    if request.method == "POST":

        profile.bkash_number = request.form.get("bkash_number")
        profile.nagad_number = request.form.get("nagad_number")

        db.session.commit()

        flash("Seller profile updated!", "success")
        return redirect(url_for("profile.seller_profile"))

    return render_template("seller_profile.html", profile=profile)