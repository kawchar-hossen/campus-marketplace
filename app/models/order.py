from app import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = "orders"

    # =========================
    # PRIMARY KEY
    # =========================
    id = db.Column(db.Integer, primary_key=True)

    # =========================
    # FOREIGN KEYS
    # =========================
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    # =========================
    # PAYMENT INFO
    # =========================
    payment_method = db.Column(db.String(20))  # cod / bkash / nagad
    trxid = db.Column(db.String(30), nullable=True)
    payment_screenshot = db.Column(db.String(255), nullable=True)

    # =========================
    # STATUS
    # =========================
    status = db.Column(db.String(20), default="pending", nullable=False)
    # pending → waiting_verification → paid → completed / cancelled

    # =========================
    # TIMESTAMP
    # =========================
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # =========================
    # RELATIONSHIPS (IMPORTANT: use back_populates ONLY)
    # =========================

    product = db.relationship(
        "Product",
        back_populates="orders"
    )

    buyer = db.relationship(
        "User",
        foreign_keys=[buyer_id],
        back_populates="buyer_orders"
    )

    seller = db.relationship(
        "User",
        foreign_keys=[seller_id],
        back_populates="seller_orders"
    )

    def __repr__(self):
        return f"<Order {self.id} - {self.status}>"