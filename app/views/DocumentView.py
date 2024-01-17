from quart.views import MethodView
from quart import request, Response
from app.helper.embeddings.embeddings_helper import EmbeddingsHelper, LLM
from app.repository.document_repo import DocumentRepository
from quart import render_template
from quart import url_for


class DocumentView(MethodView):
    def __init__(self, curator: EmbeddingsHelper, llm: LLM, document_repo: DocumentRepository) -> None:
        self.curator = curator
        self.llm = llm
        self.document_repo = document_repo

    async def post(self) -> None:
        print('post request')
        print(request)
        print("request headers")
        print(request.headers)

        form_data = await request.form
        form_dict = dict(form_data)

        link = form_dict['link']

        docs = await self.curator.get_single_article_documents(link)

        if docs is not None:
            await self.document_repo.insert_canonical_doc(docs.canonical_doc)
            await self.document_repo.insert_embedding_docs(docs.embedding_docs)

        doc_links = await self.document_repo.get_all_canonical_links()

        return await render_template('documents.html', doc_links=doc_links, submit_url=url_for('main.add-document'))

    async def get(self) -> None:
        query = request.args.get('query')
        embedding_response = await self.llm.get_embedding(query)
        embeddings = embedding_response.data[0].embedding
        return await self.document_repo.search_docs(embeddings=embeddings)
