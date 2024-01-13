from flask import Flask

from .config import Config
from dotenv import load_dotenv
from src.repository.database_engine import DatabaseEngine

from flask import g


def init_db(config: Config):
    if not hasattr(g, 'db'):
        g.db = DatabaseEngine(
            config.SQLALCHEMY_DATABASE_URI, config.ASYNC_PG_URI)

    return g.db


def create_app(config=Config):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config)

    with app.app_context():
        db = init_db(config)

        from .routes import bp as routes_bp
        app.register_blueprint(routes_bp)

    return app
