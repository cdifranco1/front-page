from flask import Flask

from .config import Config
from .extensions import db
from dotenv import load_dotenv
from flask_cors import CORS

from src.integrations.curator import Curator, Scraper, LLM

db_engine = create_async_engine(

)


def create_app(config_class=Config):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # CORS(app, resources={r"/api/*": {"origins": "*"}})
    # Use your own URI
    # print(app.config['SQLALCHEMY_DATABASE_URI'])
    db.init_app(app)

    with app.app_context():
        app.llm = LLM()
        app.scraper = Scraper(llm=app.llm)
        app.curator = Curator(llm=app.llm, scraper=app.scraper)

        from .repository.model import CanonicalDocument, EmbeddingDocument
        db.create_all()

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
