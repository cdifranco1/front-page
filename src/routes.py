from flask import Blueprint
from src.repository.document_repo import DocumentRepository
from src.integrations.curator import Curator, Scraper, LLM
from openai.types import CreateEmbeddingResponse
import json
from typing import List

bp = Blueprint('main', __name__)


@bp.route('/')
async def fetch_articles():
    llm = LLM()
    scraper = Scraper()
    curator = Curator(llm=llm, scraper=scraper)

    # dummy_documents = [Document(id='random_id', canonical_doc_id='1', content='This is a dummy document', embeddings=[
    #                             0.1, 0.2, 0.3])]
    embeddings_resp: List[CreateEmbeddingResponse] = await curator.gather_article_embeddings(
        "https://paulgraham.com")

    print(embeddings_resp)
    # with open("embeddings.txt", "w") as f:
    #     f.write(embeddings_resp[0].data)

    # print(embeddings_resp[0]["data"].keys())

    # print(embeddings)

    # document_repo = DocumentRepository()
    # document_repo.insert_docs()

    # all_docs = document_repo.get_all()

    # print(f"Total documents: {len(all_docs)}")
    # print(all_docs)

    return 'Successfully persisted documents'
