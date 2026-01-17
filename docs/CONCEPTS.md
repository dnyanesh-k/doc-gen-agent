# Doc-Gen-Agent: Core Concepts & Pipeline

## Pipeline Overview

The doc-gen-agent follows a 7-stage pipeline from code changes to generated documentation.

## Stage 1: Ingestion

**Purpose**: Detect and capture code changes

**Components**:
- **Git Diff**: Identifies modified files by comparing git commits
- **Change Analyzer**: Analyzes what changed (added, modified, deleted files)

**Output**: List of changed files with their modification status

**Learning Concepts**:
- Git operations (diff, status)
- File system operations
- Change detection algorithms

---

## Stage 2: Preprocessing

**Purpose**: Understand the nature of changes and determine documentation needs

**Components**:
- **File Pattern Matcher**: Matches file paths to patterns (e.g., `src/**/*.py` → LLD)
- **Code Parser (AST)**: Parses source code into Abstract Syntax Tree to extract structure
- **Change Categorizer**: Classifies changes (feature, bugfix, config, database, test)
- **Doc Type Detector**: Determines required documentation types (HLD, LLD, ERD, deployment, runbook)

**Output**: Categorized changes with required doc types

**Learning Concepts**:
- Glob pattern matching
- Abstract Syntax Trees (AST)
- Code structure analysis
- Classification algorithms

---

## Stage 3: Feature Extraction

**Purpose**: Prepare code for embedding and AI processing

**Components**:
- **Code Chunker**: Splits large files into smaller, manageable chunks
- **Tokenizer**: Counts tokens in code chunks (manages context window limits)
- **Embedding Generator**: Converts code chunks into vector embeddings

**Output**: Code chunks as embedding vectors (numerical representations)

**Learning Concepts**:
- Tokenization (text → tokens)
- Chunking strategies (fixed-size, semantic, sliding window)
- Embeddings (code → vectors)
- Context window management
- Vector mathematics

---

## Stage 4: Indexing

**Purpose**: Store embeddings for fast similarity search

**Components**:
- **PostgreSQL + pgvector**: Vector database for storing embeddings
- **Semantic Index**: Index structure for fast similarity queries (IVFFlat, HNSW)

**Output**: Indexed embeddings in vector database

**Learning Concepts**:
- Vector databases
- PostgreSQL extensions (pgvector)
- Index structures (IVFFlat, HNSW)
- Database schema design
- Vector indexing algorithms

---

## Stage 5: Retrieval & Augmentation

**Purpose**: Find similar code and build context for generation

**Components**:
- **Query Embedding**: Convert current code change to embedding vector
- **Similarity Search**: Find most similar code chunks using cosine similarity
- **Context Retrieval**: Retrieve relevant code examples from vector database

**Output**: Retrieved code context (similar examples)

**Learning Concepts**:
- Semantic search
- Cosine similarity
- Vector similarity algorithms
- RAG (Retrieval Augmented Generation)
- Top-K retrieval

---

## Stage 6: Generation

**Purpose**: Generate documentation using AI

**Components**:
- **Context Builder**: Assembles retrieved context, change summary, and metadata
- **Prompt Generation**: Creates structured prompts from templates
- **Prompt Templates**: Pre-defined templates for different doc types (HLD, LLD, ERD)
- **AI/LLM (Cursor AI/Claude)**: Generates documentation from prompts

**Output**: Generated documentation in Markdown format

**Learning Concepts**:
- Prompt engineering
- Few-shot learning
- Chain-of-thought prompting
- Temperature & sampling
- Streaming responses
- Context window optimization

---

## Stage 7: Post-Processing

**Purpose**: Save and distribute generated documentation

**Components**:
- **File Writer**: Saves documentation to local files (Markdown)
- **Confluence Sync**: Syncs documentation to Confluence via MCP (future)

**Output**: Documentation files saved locally and/or in Confluence

**Learning Concepts**:
- File I/O operations
- Markdown formatting
- API integration (Confluence)
- MCP (Model Context Protocol)

---

## Data Flow
