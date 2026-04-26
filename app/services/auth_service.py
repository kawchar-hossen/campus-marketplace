from app.models.user import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


def register_user(data):
    user = User(
        email=data["email"],
        password=generate_password_hash(data["password"])
    )
    db.session.add(user)
    db.session.commit()
    return user


def login_user_check(email, password):
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        return user

    return None