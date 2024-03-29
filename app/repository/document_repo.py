from app.repository.model import CanonicalDocument, EmbeddingDocument
from app.repository.database_engine import DatabaseEngine
import json


class DocumentRepository:
    def __init__(self, db_engine: DatabaseEngine):
        self.db = db_engine

    async def insert_canonical_doc(self, doc: CanonicalDocument):
        statement = """INSERT INTO canonical_documents (id, url) VALUES ($1, $2) ON CONFLICT DO NOTHING"""
        await self.db.execute(statement, doc.id, doc.url)

    async def insert_embedding_docs(self, docs: list[EmbeddingDocument]):
        statement = """
            INSERT INTO embedding_documents (id, canonical_doc_id, content, embeddings) 
            VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING
        """
        rows = [(doc.id, doc.canonical_doc_id, doc.content, f"{doc.embeddings}")
                for doc in docs]
        await self.db.executemany(statement, rows)

    async def search_docs(self, embeddings: list[float], limit: int = 10):
        statement = f"""
        SELECT canonical.url
        FROM embedding_documents embed_docs inner join canonical_documents canonical on embed_docs.canonical_doc_id = canonical.id
        ORDER BY embeddings <-> $1
        LIMIT $2;
        """
        canonical_urls = await self.db.fetch(statement, str(embeddings), limit)

        return json.dumps(list(set([r['url'] for r in canonical_urls])))

    async def get_all_canonical_links(self):
        statement = f"""
        SELECT * FROM canonical_documents;
        """
        results = await self.db.fetch(statement)
        return [r['url'] for r in results]
