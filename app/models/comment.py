from datetime import datetime
from app import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    # 🔥 Reply system (self relationship)
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # =========================
    # RELATIONSHIPS (FIXED)
    # =========================

    # 💬 User
    user = db.relationship("User", back_populates="comments")

    # 🔁 Replies (self-relation is OK with backref)
    replies = db.relationship(
        "Comment",
        backref=db.backref("parent", remote_side=[id]),
        cascade="all, delete-orphan"
    )

    # ❤️ Reactions
    reactions = db.relationship(
        "CommentReaction",
        back_populates="comment",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Comment {self.id}>"