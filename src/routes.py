from src.integrations.llm import LLM
from flask import Blueprint
from src.integrations.curator import Curator, Scraper
from src.repository.document_repo import DocumentRepository
from flask import g
from flask.views import MethodView
from flask import request


bp = Blueprint('main', __name__)


class DocumentView(MethodView):
    def __init__(self, curator: Curator, document_repo: DocumentRepository) -> None:
        self.curator = curator
        self.document_repo = document_repo

    async def post(self) -> None:
        print("Received request")
        print(request.json)
        print()

        link = request.json["link"]
        docs = await self.curator.get_single_article_documents(link)
        await self.document_repo.insert_canonical_doc(docs.canonical_doc)
        await self.document_repo.insert_embedding_docs(docs.embedding_docs)

        return 'Successfully added link'


llm = LLM()
scraper = Scraper(llm=llm)
document_repo = DocumentRepository(db_engine=g.db)
curator = Curator(llm=llm, scraper=scraper)
# document_view = DocumentView(
#     curator=Curator(llm=llm, scraper=scraper), document_repo=document_repo)

bp.add_url_rule('/add-link', methods=['POST'], view_func=DocumentView.as_view(
    'add-link', curator=curator, document_repo=document_repo))

# async def add_link():
# link = request.get_json()["link"]
# docs = await app.curator.get_single_article_documents(link)

# db.session.merge(docs.canonical_doc)
# for doc in docs.embedding_docs:
#     db.session.merge(doc)
# db.session.commit()
# db.session.remove()

# return 'Successfully added link'


# @bp.route('/')
# async def fetch_articles():
#     llm = LLM()
#     scraper = Scraper(llm=llm)

#     curator = Curator(llm=llm, scraper=scraper)

# dummy_documents = [Document(id='random_id', canonical_doc_id='1', content='This is a dummy document', embeddings=[
#                             0.1, 0.2, 0.3])]
# embeddings_resp: List[CreateEmbeddingResponse] = await curator.gather_article_embeddings(
#     "https://paulgraham.com")

# colin_docs: List[UrlDocs] = await curator.gather_article_embeddings("https://blog.colinbreck.com/")
# pg_docs: List[UrlDocs] = await curator.gather_article_embeddings("https://paulgraham.com")

# pg_scraped = await scraper.scrape_site("https://paulgraham.com")
# print(pg_scraped)

# canonical_doc_repo.insert_docs(map(lambda x: x.canonical_doc, colin_docs))
# canonical_doc_repo.insert_docs(map(lambda x: x.canonical_doc, pg_docs))

# embedding_docs = []
# for d in colin_docs:
#     for embedding in d.embedding_docs:
#         embedding_docs.append(embedding)
# embeddings_doc_repo.insert_docs(embedding_docs)

# embedding_docs = []
# for d in pg_docs:
#     for embedding in d.embedding_docs:
#         embedding_docs.append(embedding)
# embeddings_doc_repo.insert_docs(embedding_docs)

# print(docs)

# canonical_docs = [CanonicalDocument(
#     url=x.data[0].embedding) for x in embeddings_resp]

# print(embeddings_resp[0])

# with open("embeddings.txt", "w") as f:
#     f.write(str(embeddings_resp[0]))

# print(embeddings_resp[0]["data"].keys())

# print(embeddings)

# document_repo = DocumentRepository()
# document_repo.insert_docs()

# all_docs = document_repo.get_all()

# print(f"Total documents: {len(all_docs)}")
# print(all_docs)

# return 'Successfully persisted documents'
