from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    university = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    profile_image = db.Column(db.String(255), default="default.png")

    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)

    # =========================
    # RELATIONSHIPS (FIXED)
    # =========================

    products = db.relationship("Product", backref="seller", lazy=True)
    orders = db.relationship("Order", backref="buyer", lazy=True)

    # 💬 Comments
    comments = db.relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    # ❤️ Reactions
    comment_reactions = db.relationship(
        "CommentReaction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<User {self.email}>"