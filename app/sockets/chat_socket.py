from flask_socketio import emit, join_room
from flask_login import current_user
from app import db
from app.models.message import Message

def room_id(a, b):
    users = sorted([a, b])
    return f"chat_{users[0]}_{users[1]}"

def register_socket_events(socketio):

    @socketio.on("join")
    def on_join(data):
        receiver_id = int(data["receiver_id"])
        room = room_id(current_user.id, receiver_id)
        join_room(room)

    @socketio.on("send_message")
    def handle_message(data):
        receiver_id = int(data["receiver_id"])
        text = data["text"]

        room = room_id(current_user.id, receiver_id)

        msg = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            text=text
        )

        db.session.add(msg)
        db.session.commit()

        emit("receive_message", {
            "sender": current_user.full_name,
            "text": text
        }, room=room)