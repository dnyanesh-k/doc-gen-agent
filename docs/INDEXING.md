# Indexing: Vector Database for Fast Similarity Search

## What is Indexing?

### Simple Analogy: Library Book Index

**Without Index:** Check all 1 million books one by one → Takes FOREVER

**With Index:** Look up "Authentication" in index → Points to Book #4521, #8923 → Takes SECONDS

---

## Why Do We Need Indexing?

| Without Index | With Index |
|---------------|------------|
| Search ALL vectors | Search only relevant subset |
| O(n) - slow as data grows | O(log n) - stays fast |
| 10s for 100K vectors | 10ms for 100K vectors |

---

## How Vector Indexing Works

Organize similar vectors into buckets/clusters:

```
                    Vector Space
                         ↑
      Bucket A           │         Bucket B
    ┌─────────┐          │       ┌─────────┐
    │ ● ●     │ Auth     │       │    ● ●  │ Database
    │   ● ●   │ code     │       │  ●   ●  │ code
    └─────────┘          │       └─────────┘
    ─────────────────────┼─────────────────────→
      Bucket C           │         Bucket D
    ┌─────────┐          │       ┌─────────┐
    │ ●  ●    │ UI       │       │   ●  ●  │ Config
    │    ● ●  │ code     │       │ ●    ●  │ code
    └─────────┘          │       └─────────┘

Search for "auth code" → Only search Bucket A (not B, C, D)
```

---

## Index Types (pgvector)

### IVFFlat (Inverted File Index)
- Divides vectors into clusters
- Search only nearby clusters
- **Pros:** Fast to build
- **Cons:** Less accurate

### HNSW (Hierarchical Navigable Small World)
- Creates graph connecting similar vectors
- Navigates via "shortcuts"
- **Pros:** Very accurate, faster search
- **Cons:** Slower to build, more memory

---

## PostgreSQL + pgvector Implementation

### Schema
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE code_embeddings (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_content TEXT NOT NULL,
    embedding vector(384),  -- 384 dims for all-MiniLM-L6-v2
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index
CREATE INDEX ON code_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Similarity Search
```sql
SELECT file_path, chunk_content,
       1 - (embedding <=> query_embedding) AS similarity
FROM code_embeddings
ORDER BY embedding <=> query_embedding
LIMIT 5;
```

---

## Industry Use Cases

| Company | Use Case | Scale |
|---------|----------|-------|
| GitHub Copilot | Similar code patterns | Billions of files |
| Google Search | Semantic search | Trillions of docs |
| Spotify | Song recommendations | 100M+ songs |
| Netflix | Movie recommendations | 15K+ titles |

---

## Our Implementation

```
src/indexing/
├── __init__.py
├── database.py      # PostgreSQL connection
├── schema.py        # Create tables, indexes
└── operations.py    # Insert, search embeddings
```

### Flow
```
Code Change
    ↓
[Feature Extraction] → Embedding [0.12, -0.45, ...]
    ↓
[Indexing] → Store in PostgreSQL + pgvector
    ↓
[Retrieval] → Search similar code (fast!)
    ↓
[Generation] → LLM gets context → Better docs
```

---

## Quick Reference

| Concept | Description |
|---------|-------------|
| **Index** | Organized lookup for fast search |
| **Vector Index** | Groups similar vectors together |
| **IVFFlat** | Cluster-based index |
| **HNSW** | Graph-based index |
| **pgvector** | PostgreSQL vector extension |
| **Cosine Distance** | `<=>` operator in pgvector |
