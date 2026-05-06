from app import db
from datetime import datetime


class SellerProfile(db.Model):
    __tablename__ = "seller_profiles"

    # =========================
    # PRIMARY KEY
    # =========================
    id = db.Column(db.Integer, primary_key=True)

    # =========================
    # FOREIGN KEY (1–1 with User)
    # =========================
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    # =========================
    # PAYMENT INFO
    # =========================
    bkash_number = db.Column(db.String(20))
    nagad_number = db.Column(db.String(20))

    # =========================
    # TIMESTAMP
    # =========================
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # =========================
    # RELATIONSHIP (IMPORTANT)
    # =========================
    user = db.relationship(
        "User",
        back_populates="seller_profile"
    )

    def __repr__(self):
        return f"<SellerProfile UserID={self.user_id}>"