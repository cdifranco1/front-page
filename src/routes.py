from flask import Blueprint

bp = Blueprint('main', __name__)


@bp.route('/')
def fetch_articles():
    return 'Articles fetched!'
