from app import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = "products"

    # =========================
    # PRIMARY KEY
    # =========================
    id = db.Column(db.Integer, primary_key=True)

    # =========================
    # PRODUCT INFO
    # =========================
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80))
    image = db.Column(db.String(255), default="default_product.png")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # =========================
    # FOREIGN KEY
    # =========================
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # =========================
    # RELATIONSHIPS
    # =========================

    # Seller (User ↔ Product)
    seller = db.relationship(
        "User",
        back_populates="products"
    )

    # Orders for this product
    orders = db.relationship(
        "Order",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    # Comments
    comments = db.relationship(
        "Comment",
        backref="product",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Product {self.title}>"