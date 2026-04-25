from app import db


class Wishlist(db.Model):
    __tablename__ = "wishlists"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    # Relationship with User
    user = db.relationship(
        "User",
        backref=db.backref(
            "wishlist_items",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    # Relationship with Product
    product = db.relationship(
        "Product",
        backref=db.backref(
            "wishlist_items",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Wishlist User:{self.user_id} Product:{self.product_id}>"