from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))

    status = db.Column(db.String(50), default="Pending")
    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product", backref="orders")