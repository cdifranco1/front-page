import asyncpg
from src.repository.model import CanonicalDocument, EmbeddingDocument


class DatabaseEngine:
    def __init__(self, asyncpg_uri: str) -> None:
        self.asyncpg_uri = asyncpg_uri
        self.connection_pool = None

    async def init_connection_pool(self) -> None:
        self.connection_pool = await asyncpg.create_pool(self.asyncpg_uri)

    async def execute(self, statement: str, *args) -> None:
        async with self.connection_pool.acquire() as conn:
            await conn.execute(statement, *args)

    async def executemany(self, statement: str, *args) -> None:
        async with self.connection_pool.acquire() as conn:
            await conn.executemany(statement, *args)

    async def close(self):
        return await self.connection_pool.terminate()


class DocumentRepository:
    def __init__(self, db_engine: DatabaseEngine):
        self.db = db_engine

    async def insert_canonical_doc_v2(self, doc: CanonicalDocument):
        statement = """INSERT INTO canonical_documents (id, url) VALUES ($1, $2) ON CONFLICT DO NOTHING"""
        await self.db.execute(statement, doc.id, doc.url)

    async def insert_embedding_docs_v2(self, docs: list[EmbeddingDocument]):
        statement = """
            INSERT INTO embedding_documents (id, canonical_doc_id, content, embeddings) 
            VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING
        """
        rows = [(doc.id, doc.canonical_doc_id, doc.content, f"{doc.embeddings}")
                for doc in docs]
        await self.db.executemany(statement, rows)