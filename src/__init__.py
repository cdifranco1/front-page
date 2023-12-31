from flask import Flask

from .config import Config
from .extensions import db
from dotenv import load_dotenv
from flask_cors import CORS


def create_app(config_class=Config):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # CORS(app, resources={r"/api/*": {"origins": "*"}})
    # Use your own URI
    # print(app.config['SQLALCHEMY_DATABASE_URI'])
    db.init_app(app)

    with app.app_context():
        from .repository.model import Document
        db.create_all()

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
