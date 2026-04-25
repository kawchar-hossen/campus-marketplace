from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.user import User
from app.models.message import Message

chat = Blueprint("chat", __name__)

@chat.route("/chat/<int:user_id>")
@login_required
def private_chat(user_id):
    other_user = User.query.get_or_404(user_id)

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) &
         (Message.receiver_id == user_id)) |

        ((Message.sender_id == user_id) &
         (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    return render_template(
        "chat.html",
        other_user=other_user,
        messages=messages
    )