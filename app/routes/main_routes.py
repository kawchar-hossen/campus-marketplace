from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user

from app import db
from app.models.product import Product
from app.models.comment import Comment
from app.models.comment_reaction import CommentReaction
from sqlalchemy import func


main = Blueprint("main", __name__)


# 🔥 Helper function
def get_reaction_counts(comment_id):

    rows = db.session.query(
        CommentReaction.reaction,
        func.count(CommentReaction.id)
    ).filter_by(comment_id=comment_id).group_by(CommentReaction.reaction).all()

    result = {
        "like": 0,
        "love": 0,
        "haha": 0,
        "wow": 0,
        "sad": 0,
        "angry": 0
    }

    for reaction, count in rows:
        result[reaction] = count

    return result

# =========================
# HOME PAGE
# =========================
@main.route("/")
def home():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("index.html", products=products)


# =========================
# PRODUCT DETAIL + COMMENTS + REPLIES
# =========================
@main.route("/product/<int:product_id>", methods=["GET", "POST"])
def product_detail(product_id):

    product = Product.query.get_or_404(product_id)

    # =========================
    # POST COMMENT / REPLY
    # =========================
    if request.method == "POST":

        if not current_user.is_authenticated:
            flash("Login required", "danger")
            return redirect(url_for("auth.login"))

        text = request.form.get("comment", "").strip()
        parent_id = request.form.get("parent_id")  # 🔥 reply support

        # validation
        if not text:
            flash("Comment cannot be empty", "warning")
            return redirect(request.url)

        if len(text) < 2:
            flash("Comment is too short", "warning")
            return redirect(request.url)

        if len(text) > 500:
            flash("Comment too long (max 500 chars)", "warning")
            return redirect(request.url)

        # create comment (supports replies)
        comment = Comment(
            text=text,
            user_id=current_user.id,
            product_id=product.id,
            parent_id=int(parent_id) if parent_id else None
        )

        db.session.add(comment)
        db.session.commit()

        flash("Comment posted!", "success")
        return redirect(request.url)

    # =========================
    # GET TOP-LEVEL COMMENTS ONLY
    # =========================
    comments = Comment.query.filter_by(
        product_id=product.id,
        parent_id=None
    ).order_by(Comment.created_at.desc()).all()

    return render_template(
        "product_detail.html",
        product=product,
        comments=comments
    )






@main.route("/comment/react/<int:comment_id>", methods=["POST"])
def react_comment(comment_id):

    if not current_user.is_authenticated:
        return jsonify({"error": "login_required"}), 401

    # ensure comment exists
    Comment.query.get_or_404(comment_id)

    data = request.get_json() or {}
    reaction_type = data.get("reaction")

    valid_reactions = ["like", "love", "haha", "wow", "sad", "angry"]

    if reaction_type not in valid_reactions:
        return jsonify({"error": "invalid_reaction"}), 400

    existing = CommentReaction.query.filter_by(
        user_id=current_user.id,
        comment_id=comment_id
    ).first()

    # =========================
    # TOGGLE LOGIC (FIXED)
    # =========================
    if existing:
        if existing.reaction == reaction_type:
            db.session.delete(existing)
        else:
            existing.reaction = reaction_type
    else:
        new_reaction = CommentReaction(
            user_id=current_user.id,
            comment_id=comment_id,
            reaction=reaction_type
        )
        db.session.add(new_reaction)

    db.session.commit()

    # 🔥 recompute after commit (important fix)
    existing_reaction = CommentReaction.query.filter_by(
        user_id=current_user.id,
        comment_id=comment_id
    ).first()

    return jsonify({
        "success": True,
        "counts": get_reaction_counts(comment_id),
        "user_reaction": existing_reaction.reaction if existing_reaction else None
    })