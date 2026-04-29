import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO


# =====================================
# Extensions
# =====================================

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Keep simple here
socketio = SocketIO()


# =====================================
# Flask-Login Config
# =====================================

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


# =====================================
# Create App Factory
# =====================================

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static"
    )

    # =====================================
    # Load Config
    # =====================================

    app.config.from_object("app.utils.config.Config")

    app.config["UPLOAD_FOLDER"] = os.path.abspath("static/images")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    app.config.setdefault("SECRET_KEY", "super-secret-key")
    app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///campus_marketplace.db"
    )
    app.config.setdefault(
        "SQLALCHEMY_TRACK_MODIFICATIONS",
        False
    )

    # =====================================
    # Initialize Extensions
    # =====================================

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # IMPORTANT
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode="threading"
    )

    # =====================================
    # Import Models
    # =====================================

    from app.models import User, Product, Wishlist, Order, Message

    # =====================================
    # User Loader
    # =====================================

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # =====================================
    # Import Blueprints
    # =====================================

    from app.routes.main_routes import main
    from app.routes.auth_routes import auth
    from app.routes.product_routes import product
    from app.routes.wishlist_routes import wishlist
    from app.routes.chat_routes import chat
    from app.routes.order_routes import order
    from app.routes.admin_routes import admin

    # =====================================
    # Register Blueprints
    # =====================================

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(product)
    app.register_blueprint(wishlist)
    app.register_blueprint(chat)
    app.register_blueprint(order)
    app.register_blueprint(admin)

    # =====================================
    # Import Socket Events
    # VERY IMPORTANT
    # =====================================

    from app.sockets import chat_socket

    return app