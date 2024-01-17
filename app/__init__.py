from quart import Quart

from .config import Config
from dotenv import load_dotenv
from app.repository.database_engine import DatabaseEngine
from quart import Blueprint

from app.common.llm import LLM
from quart import Blueprint
from app.helper.embeddings.embeddings_helper import EmbeddingsHelper, Scraper
from app.repository.database_engine import DatabaseEngine
from app.repository.document_repo import DocumentRepository
from app.views.DocumentView import DocumentView
from app.views.HomeView import HomeView


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
    curator = EmbeddingsHelper(llm=llm, scraper=scraper)
    document_repo = DocumentRepository(db_engine=app.db_engine)

    bp.add_url_rule('/documents', methods=['POST', 'GET'], view_func=DocumentView.as_view(
        'add-document', curator=curator, document_repo=document_repo, llm=llm))
    bp.add_url_rule('/', methods=['GET'], view_func=HomeView.as_view(
        'home', curator=curator, document_repo=document_repo, llm=llm))

    app.register_blueprint(bp)

    return app


app = create_app()
