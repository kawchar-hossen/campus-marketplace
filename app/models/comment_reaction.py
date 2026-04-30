from app import db


class CommentReaction(db.Model):
    __tablename__ = "comment_reactions"

    id = db.Column(db.Integer, primary_key=True)

    reaction = db.Column(db.String(10), nullable=False)

    # =========================
    # FOREIGN KEYS
    # =========================
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=False)

    # =========================
    # RELATIONSHIPS (FIXED)
    # =========================
    user = db.relationship("User", back_populates="comment_reactions")
    comment = db.relationship("Comment", back_populates="reactions")

    def __repr__(self):
        return f"<CommentReaction {self.reaction}>"