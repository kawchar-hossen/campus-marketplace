# =====================================
# app/sockets/chat_socket.py
# =====================================

from flask_socketio import emit, join_room
from flask_login import current_user

from app import socketio, db
from app.models.chat import Message


# =====================================
# Join Personal Room
# =====================================
@socketio.on("join")
def handle_join(data):
    """
    Every authenticated user joins
    their own private room using
    their user ID.
    """

    if not current_user.is_authenticated:
        return

    room = str(current_user.id)
    join_room(room)

    print(f"{current_user.full_name} joined room: {room}")


# =====================================
# Send Private Message
# =====================================
@socketio.on("send_message")
def handle_send_message(data):
    """
    Frontend sends:
    {
        "receiver_id": 9,
        "text": "Hello"
    }
    """

    if not current_user.is_authenticated:
        return

    receiver_id = int(data["receiver_id"])
    text = data["text"].strip()

    # Prevent empty messages
    if not text:
        return

    # Save message to database
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        text=text
    )

    db.session.add(message)
    db.session.commit()

    payload = {
        "sender": current_user.full_name,
        "sender_id": current_user.id,
        "receiver_id": receiver_id,
        "text": text
    }

    # Send to receiver
    emit(
        "receive_message",
        payload,
        room=str(receiver_id)
    )

    # Send back to sender
    emit(
        "receive_message",
        payload,
        room=str(current_user.id)
    )

    print(
        f"Message sent from User {current_user.id} "
        f"to User {receiver_id}: {text}"
    )