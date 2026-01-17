# Doc-Agent: Step-by-Step Learning Plan

## 🎯 Goal
Build an AI-powered documentation agent that analyzes code changes and generates documentation using Cursor AI

## 📚 AI Concepts We'll Learn

1. **Tokenization**: Breaking text into tokens for AI processing
2. **Embeddings**: Converting code/text to vector representations
3. **Vector Databases**: Storing and querying embeddings (PostgreSQL + pgvector)
4. **Semantic Search**: Finding similar code using vector similarity
5. **RAG (Retrieval Augmented Generation)**: Using retrieved context to generate better docs
6. **Prompt Engineering**: Crafting effective prompts for AI
7. **Context Window Management**: Handling large codebases efficiently
8. **Chain-of-Thought**: Breaking complex tasks into steps
9. **Few-Shot Learning**: Using examples in prompts
10. **Temperature & Sampling**: Controlling AI output randomness
11. **Streaming Responses**: Handling real-time AI output
12. **Chunking Strategies**: Splitting large code into manageable pieces

## 🏗️ Architecture Overview

```
Code Changes → Change Analyzer → Context Builder → Prompt Generator → Cursor AI → Documentation
```

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **AI Engine**: Cursor AI (Claude via Composer)
- **Vector Database**: PostgreSQL + pgvector extension
- **Code Analysis**: Git diff, AST parsing
- **Text Processing**: Token counting, chunking
- **Embeddings**: OpenAI/Claude embeddings or sentence-transformers
- **Storage**: PostgreSQL (vectors) + Local files (Markdown)
- **Future**: Confluence MCP (after learning basics)

## 📋 Step-by-Step Build Plan

### Phase 1: Foundation (Learning: Git, File I/O)
- [ ] Step 1.1: Project structure
- [ ] Step 1.2: Git change detection
- [ ] Step 1.3: File pattern matching
- [ ] Step 1.4: Basic config system

### Phase 2: Code Analysis (Learning: AST, Parsing)
- [ ] Step 2.1: Parse changed files
- [ ] Step 2.2: Extract code structure
- [ ] Step 2.3: Identify doc types needed
- [ ] Step 2.4: Build change summary

### Phase 3: Tokenization & Context (Learning: Tokenization, Chunking)
- [ ] Step 3.1: Count tokens in code
- [ ] Step 3.2: Chunk large files
- [ ] Step 3.3: Build context window
- [ ] Step 3.4: Manage token limits

### Phase 4: Prompt Engineering (Learning: Prompt Design)
- [ ] Step 4.1: Create prompt templates
- [ ] Step 4.2: Inject code context
- [ ] Step 4.3: Structure prompts
- [ ] Step 4.4: Test prompt effectiveness

### Phase 5: Vector Database Setup (Learning: PostgreSQL, pgvector)
- [ ] Step 5.1: Install PostgreSQL + pgvector
- [ ] Step 5.2: Create database schema for embeddings
- [ ] Step 5.3: Store code embeddings in vector DB
- [ ] Step 5.4: Query similar code using vector search

### Phase 6: Embeddings & Semantic Search (Learning: Embeddings, Vector Math)
- [ ] Step 6.1: Generate code embeddings
- [ ] Step 6.2: Store embeddings in PostgreSQL
- [ ] Step 6.3: Implement semantic search (cosine similarity)
- [ ] Step 6.4: Retrieve relevant code context

### Phase 7: RAG Implementation (Learning: RAG, Context Augmentation)
- [ ] Step 7.1: Extract code features
- [ ] Step 7.2: Build RAG pipeline
- [ ] Step 7.3: Retrieve relevant context from vector DB
- [ ] Step 7.4: Augment prompts with retrieved context

### Phase 8: AI Integration (Learning: API Usage, Streaming)
- [ ] Step 8.1: Integrate with Cursor Composer
- [ ] Step 8.2: Stream responses
- [ ] Step 8.3: Handle errors
- [ ] Step 8.4: Save generated docs

### Phase 9: Optimization (Learning: Caching, Batching, Indexing)
- [ ] Step 9.1: Cache parsed code and embeddings
- [ ] Step 9.2: Batch similar changes
- [ ] Step 9.3: Optimize vector DB queries (indexes)
- [ ] Step 9.4: Performance tuning

## 🎓 Learning Path Per Step

Each step will include:
1. **Concept Explanation**: What we're learning
2. **Simple Example**: Minimal code to understand
3. **Implementation**: Build the feature
4. **Testing**: Verify it works
5. **Commit**: Save progress

## 📁 Proposed Structure

```
doc-gen-agent/
├── PLAN.md              # This file
├── README.md            # Project overview
├── config.yaml          # Configuration
├── src/
│   ├── __init__.py
│   ├── analyzer.py      # Code analysis
│   ├── tokenizer.py     # Token counting/chunking
│   ├── embeddings.py    # Generate embeddings
│   ├── vector_db.py     # PostgreSQL + pgvector operations
│   ├── context.py       # Context building
│   ├── prompts.py       # Prompt generation
│   └── rag.py          # RAG implementation
├── prompts/            # Prompt templates
├── tests/              # Unit tests
└── output/             # Generated docs
```

## 🚀 Next Steps

1. Create folder structure
2. Start with Step 1.1: Project structure
3. Learn and implement one concept at a time
4. Test and commit after each step
