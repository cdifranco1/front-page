from quart.views import MethodView
from quart import request
from src.curator.curator import Curator, LLM
from src.repository.database_engine import DocumentRepository


class DocumentView(MethodView):
    def __init__(self, curator: Curator, llm: LLM, document_repo: DocumentRepository) -> None:
        self.curator = curator
        self.llm = llm
        self.document_repo = document_repo

    async def post(self) -> None:
        body = await request.get_json()

        link = body["link"]
        docs = await self.curator.get_single_article_documents(link)
        await self.document_repo.insert_canonical_doc_v2(docs.canonical_doc)
        await self.document_repo.insert_embedding_docs_v2(docs.embedding_docs)

        return 'Successfully added link'

    async def get(self) -> None:
        query = request.args.get('query')
        embedding_response = await self.llm.get_embedding(query)
        embeddings = embedding_response.data[0].embedding
        return await self.document_repo.search_docs(embeddings=embeddings)
