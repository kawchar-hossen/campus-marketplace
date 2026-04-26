import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static"
        )
    app.config.from_object("app.utils.config.Config")

    app.config["UPLOAD_FOLDER"] = os.path.abspath("static/images")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    socketio.init_app(app, async_mode="threading")  # 🔥 HERE

    login_manager.login_view = "auth.login"

    from app.models import User, Product, Wishlist, Order, Message

    from app.routes.main_routes import main
    from app.routes.auth_routes import auth
    from app.routes.product_routes import product
    from app.routes.wishlist_routes import wishlist
    from app.routes.chat_routes import chat
    from app.routes.order_routes import order
    from app.routes.admin_routes import admin
    

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(product)
    app.register_blueprint(wishlist)
    app.register_blueprint(chat)
    app.register_blueprint(order)
    #app.register_blueprint(order, url_prefix="/order")
    app.register_blueprint(admin)
    

    from app.sockets.chat_socket import register_socket_events
    register_socket_events(socketio)

    return app