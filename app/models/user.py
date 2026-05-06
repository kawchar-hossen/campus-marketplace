from app import db, login_manager
from flask_login import UserMixin


# =========================
# LOGIN LOADER
# =========================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# =========================
# USER MODEL
# =========================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    # PRIMARY KEY
    id = db.Column(db.Integer, primary_key=True)

    # BASIC INFO
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    phone = db.Column(db.String(20))
    university = db.Column(db.String(120))
    profile_image = db.Column(db.String(255), default="default.png")

    # ROLE FLAGS
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)

    # =========================
    # PRODUCTS (SELLER SIDE)
    # =========================
    products = db.relationship(
        "Product",
        back_populates="seller",
        cascade="all, delete-orphan",
        lazy=True
    )

    # =========================
    # ORDERS (BUYER SIDE)
    # =========================
    buyer_orders = db.relationship(
        "Order",
        foreign_keys="Order.buyer_id",
        back_populates="buyer",
        cascade="all, delete-orphan",
        lazy=True
    )

    # =========================
    # ORDERS (SELLER SIDE)
    # =========================
    seller_orders = db.relationship(
        "Order",
        foreign_keys="Order.seller_id",
        back_populates="seller",
        cascade="all, delete-orphan",
        lazy=True
    )

    # =========================
    # COMMENTS
    # =========================
    comments = db.relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    # =========================
    # COMMENT REACTIONS
    # =========================
    comment_reactions = db.relationship(
        "CommentReaction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # =========================
    # SELLER PROFILE (1–1)
    # =========================
    seller_profile = db.relationship(
        "SellerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"