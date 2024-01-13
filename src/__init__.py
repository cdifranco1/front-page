from quart import Quart

from .config import Config
from dotenv import load_dotenv
from src.repository.database_engine import DatabaseEngine
from quart import Blueprint

from src.integrations.llm import LLM
from quart import Blueprint
from src.integrations.curator import Curator, Scraper
from src.repository.database_engine import DatabaseEngine, DocumentRepository
from src.views.DocumentView import DocumentView


def create_app(config=Config):
    load_dotenv()

    app = Quart(__name__)
    app.config.from_object(config)
    db_engine = DatabaseEngine(config.ASYNC_PG_URI)
    app.db_engine = db_engine

    @app.before_serving
    async def init_connection_pool():
        await db_engine.init_connection_pool()
        app.db = db_engine

    @app.after_serving
    async def close_connection_pool():
        await app.db.close()

    bp = Blueprint('main', __name__)

    llm = LLM()
    scraper = Scraper(llm=llm)
    curator = Curator(llm=llm, scraper=scraper)
    document_repo = DocumentRepository(db_engine=app.db_engine)
    bp.add_url_rule('/add-link', methods=['POST'], view_func=DocumentView.as_view(
        'add-link', curator=curator, document_repo=document_repo))
    app.register_blueprint(bp)

    return app
