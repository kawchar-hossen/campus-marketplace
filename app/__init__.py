import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail


# =====================================
# EXTENSIONS
# =====================================
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO()
mail = Mail()


# =====================================
# LOGIN CONFIG
# =====================================
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


# =====================================
# APP FACTORY
# =====================================
def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static"
    )

    # =====================================
    # CONFIG
    # =====================================
    app.config.from_object("app.utils.config.Config")

    app.config["UPLOAD_FOLDER"] = os.path.abspath("static/images")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    app.config.setdefault("SECRET_KEY", "super-secret-key")
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///campus_marketplace.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # =====================================
    # INIT EXTENSIONS
    # =====================================
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode="threading"
    )

    # =====================================
    # IMPORT MODELS (IMPORTANT)
    # =====================================
    from app.models.user import User
    from app.models.product import Product
    from app.models.order import Order
    from app.models.seller_profile import SellerProfile

    # Optional models (only if exist)
    # from app.models.wishlist import Wishlist
    # from app.models.message import Message

    # =====================================
    # USER LOADER (KEEP ONLY HERE)
    # =====================================
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # =====================================
    # BLUEPRINTS
    # =====================================
    from app.routes.main_routes import main
    from app.routes.auth_routes import auth
    from app.routes.product_routes import product
    from app.routes.wishlist_routes import wishlist
    from app.routes.chat_routes import chat
    from app.routes.order_routes import order
    from app.routes.payment_routes import payment
    from app.routes.seller_routes import seller
    from app.routes.admin_routes import admin
    from app.routes.profile_routes import profile

    # REGISTER BLUEPRINTS
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(product)
    app.register_blueprint(wishlist)
    app.register_blueprint(chat)
    app.register_blueprint(order)
    app.register_blueprint(payment)
    app.register_blueprint(seller)
    app.register_blueprint(admin)
    app.register_blueprint(profile)

    # =====================================
    # SOCKET EVENTS
    # =====================================
    from app.sockets import chat_socket

    return app