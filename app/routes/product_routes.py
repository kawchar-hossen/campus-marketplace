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

product = Blueprint("product", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


# --------------------------
# Helpers
# --------------------------
def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --------------------------
# All Products
# --------------------------
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

    products = query.order_by(Product.created_at.desc()).all()

    return render_template(
        "products.html",
        products=products,
        search=search,
        category=category,
        max_price=max_price
    )


# --------------------------
# Add Product
# --------------------------
@product.route("/product/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        price = request.form["price"]
        category = request.form["category"].strip()

        if not title or not price:
            flash("Title and price required.", "danger")
            return redirect("/product/add")

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
                return redirect("/product/add")

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


# --------------------------
# Product Detail
# --------------------------
@product.route("/product/<int:id>")
def product_detail(id):
    item = Product.query.get_or_404(id)
    return render_template("product_detail.html", product=item)


# --------------------------
# Edit Product
# --------------------------
@product.route("/product/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_product(id):
    item = Product.query.get_or_404(id)

    if item.seller_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect("/products")

    if request.method == "POST":
        item.title = request.form["title"].strip()
        item.description = request.form["description"].strip()
        item.price = float(request.form["price"])
        item.category = request.form["category"].strip()

        db.session.commit()

        flash("Product updated.", "success")
        return redirect(url_for("product.product_detail", id=id))

    return render_template("edit_product.html", product=item)


# --------------------------
# Delete Product
# --------------------------
@product.route("/product/delete/<int:id>")
@login_required
def delete_product(id):
    item = Product.query.get_or_404(id)

    if item.seller_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect("/products")

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
    return redirect("/products")