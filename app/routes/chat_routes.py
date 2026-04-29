# =====================================
# app/routes/chat_routes.py
# =====================================

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app import db
from app.models.user import User
from app.models.chat import Message


chat = Blueprint("chat", __name__)


# =====================================
# Private Chat Page
# =====================================
@chat.route("/chat/<int:user_id>")
@login_required
def chat_page(user_id):
    """
    Open private chat between the current
    logged-in user and another user.
    """

    # Get the other user
    other_user = User.query.get_or_404(user_id)

    # Fetch conversation history
    messages = Message.query.filter(
        (
            (Message.sender_id == current_user.id) &
            (Message.receiver_id == user_id)
        ) |
        (
            (Message.sender_id == user_id) &
            (Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()

    return render_template(
        "chat.html",
        other_user=other_user,
        messages=messages
    )




@chat.route("/messages")
@login_required
def inbox():
    # Get all users who chatted with current user
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) |
        (Message.receiver_id == current_user.id)
    ).all()

    user_ids = set()

    for msg in messages:
        user_ids.add(msg.sender_id)
        user_ids.add(msg.receiver_id)

    user_ids.discard(current_user.id)

    users = User.query.filter(User.id.in_(user_ids)).all()

    return render_template("inbox.html", users=users)