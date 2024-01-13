
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    canonical_document_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embeddings VECTOR(1536) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
)