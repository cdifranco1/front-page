from quart.views import MethodView
from quart import request, render_template
from app.helper.embeddings.embeddings_helper import EmbeddingsHelper, LLM
from app.repository.document_repo import DocumentRepository
from quart import url_for


class HomeView(MethodView):
    def __init__(self, curator: EmbeddingsHelper, llm: LLM, document_repo: DocumentRepository) -> None:
        self.curator = curator
        self.llm = llm
        self.document_repo = document_repo

    # async def post(self) -> None:
    #     body = await request.get_json()
    #     link = body["link"]
    #     docs = await self.curator.get_single_article_documents(link)
    #     await self.document_repo.insert_canonical_doc(docs.canonical_doc)
    #     await self.document_repo.insert_embedding_docs(docs.embedding_docs)
    #     return 'Successfully added link'

    async def get(self) -> None:
        doc_links = await self.document_repo.get_all_canonical_links()
        return await render_template('documents.html', doc_links=doc_links, submit_url=url_for('main.add-document'))
