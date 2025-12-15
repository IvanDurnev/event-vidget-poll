from flask import Flask
from config import Config
from .db import db, migrate
from .redis import redis_client

def create_app():
    app = Flask(
        __name__,
        template_folder=Config.TEMPLATES_FOLDER,
        static_folder=Config.STATIC_FOLDER
    )
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.main import main_bp
    from .routes.poll import poll_bp
    from .routes.screen import screen_bp
    from .routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(poll_bp)
    app.register_blueprint(screen_bp)
    app.register_blueprint(admin_bp)

    return app
