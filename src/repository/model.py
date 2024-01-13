from sqlalchemy.dialects.postgresql import TEXT
from pgvecto_rs.sqlalchemy import Vector
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

from sqlalchemy import ForeignKey


class Base(AsyncAttrs, DeclarativeBase):
    pass


class EmbeddingDocument(Base):
    __tablename__ = "embedding_documents"

    id = mapped_column("id", TEXT, primary_key=True)
    canonical_doc_id = mapped_column(
        "canonical_doc_id", TEXT, ForeignKey("canonical_documents.id"))
    content = mapped_column("content", TEXT, nullable=False)
    embeddings = mapped_column("embeddings", Vector(1536), nullable=False)
    # created_at = mapped_column(
    #     "created_at", TIMESTAMP, nullable=False, default=db.func.now())

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, canonical_doc_id={self.canonical_doc_id}, content={self.content}, embeddings={self.embeddings} >"


class CanonicalDocument(Base):
    __tablename__ = "canonical_documents"

    id = mapped_column("id", TEXT, nullable=False, primary_key=True)
    url = mapped_column("url", TEXT, nullable=False)
    # created_at = mapped_column(
    #     "created_at", TIMESTAMP, nullable=False, default=db.func.now())

    def __repr__(self) -> str:
        return f"<CanonicalDocument(id={self.id}, url={self.url}>"
