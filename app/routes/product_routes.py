import os
from uuid import uuid4

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models.product import Product
from app.models.seller_profile import SellerProfile

product = Blueprint("product", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


# =====================================
# HELPER
# =====================================
def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# =====================================
# ALL PRODUCTS
# =====================================
@product.route("/products")
def all_products():

    search = request.args.get("search", "")
    category = request.args.get("category", "")
    max_price = request.args.get("max_price", "")

    query = Product.query

    if search:
        query = query.filter(Product.title.ilike(f"%{search}%"))

    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))

    if max_price:
        try:
            query = query.filter(Product.price <= float(max_price))
        except:
            pass

    products = query.order_by(Product.id.desc()).all()

    return render_template(
        "products.html",
        products=products,
        search=search,
        category=category,
        max_price=max_price
    )


# =====================================
# ADD PRODUCT (SELLER ONLY)
# =====================================
@product.route("/product/add", methods=["GET", "POST"])
@login_required
def add_product():

    # =====================================
    # 🚨 SELLER PAYMENT PROFILE CHECK
    # =====================================
    seller_profile = SellerProfile.query.filter_by(user_id=current_user.id).first()

    if not seller_profile:
        flash("Please create seller profile first", "warning")
        return redirect(url_for("profile.seller_profile"))

    if not seller_profile.bkash_number and not seller_profile.nagad_number:
        flash("Please add payment info before selling", "warning")
        return redirect(url_for("profile.seller_profile"))

    # =====================================
    # HANDLE FORM
    # =====================================
    if request.method == "POST":

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price")
        category = request.form.get("category", "").strip()

        if not title or not price:
            flash("Title and price required.", "danger")
            return redirect(url_for("product.add_product"))

        # =====================================
        # IMAGE UPLOAD
        # =====================================
        filename = "default_product.png"
        image = request.files.get("image")

        if image and image.filename != "":
            if allowed_file(image.filename):

                ext = image.filename.rsplit(".", 1)[1].lower()
                filename = f"{uuid4().hex}.{ext}"

                path = os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    filename
                )

                image.save(path)

            else:
                flash("Invalid image format.", "danger")
                return redirect(url_for("product.add_product"))

        # =====================================
        # CREATE PRODUCT
        # =====================================
        new_product = Product(
            title=title,
            description=description,
            price=float(price),
            category=category,
            image=filename,
            seller_id=current_user.id
        )

        db.session.add(new_product)
        db.session.commit()

        flash("Product added successfully.", "success")
        return redirect(url_for("product.all_products"))

    return render_template("add_product.html")


# =====================================
# PRODUCT DETAIL
# =====================================
@product.route("/product/<int:id>")
def product_detail(id):

    item = Product.query.get_or_404(id)
    return render_template("product_detail.html", product=item)


# =====================================
# EDIT PRODUCT
# =====================================
@product.route("/product/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_product(id):

    item = Product.query.get_or_404(id)

    if item.seller_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("product.all_products"))

    if request.method == "POST":

        item.title = request.form.get("title", "").strip()
        item.description = request.form.get("description", "").strip()
        item.price = float(request.form.get("price"))
        item.category = request.form.get("category", "").strip()

        db.session.commit()

        flash("Product updated.", "success")
        return redirect(url_for("product.product_detail", id=id))

    return render_template("edit_product.html", product=item)


# =====================================
# DELETE PRODUCT
# =====================================
@product.route("/product/delete/<int:id>")
@login_required
def delete_product(id):

    item = Product.query.get_or_404(id)

    if item.seller_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("product.all_products"))

    # delete image file
    if item.image != "default_product.png":

        path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            item.image
        )

        if os.path.exists(path):
            os.remove(path)

    db.session.delete(item)
    db.session.commit()

    flash("Product deleted.", "info")
    return redirect(url_for("product.all_products"))