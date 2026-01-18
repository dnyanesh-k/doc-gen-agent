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

```
Code Changes
    ↓
[Ingestion] → Changed Files
    ↓
[Preprocessing] → Categorized Changes + Doc Types
    ↓
[Feature Extraction] → Code Chunks + Embeddings
    ↓
[Indexing] → Stored in Vector DB
    ↓
[Retrieval & Augmentation] → Similar Code Context
    ↓
[Generation] → Documentation (Markdown)
    ↓
[Post-Processing] → Saved Files / Confluence
```

## Key Concepts - Detailed Explanations

---

### 1. CHUNKS (Code Chunking)

#### Basic: What is a Chunk?
A **chunk** is a small piece of code cut from a larger file.

Think of it like cutting a long book into chapters. Instead of reading 500 pages at once, you read one chapter at a time.

```
Large File (1000 lines)
         ↓
    Split into chunks
         ↓
┌─────────┬─────────┬─────────┐
│ Chunk 1 │ Chunk 2 │ Chunk 3 │
│ 300 lines│ 350 lines│ 350 lines│
└─────────┴─────────┴─────────┘
```

#### Why Do We Need Chunks?
- **LLMs have limits**: Can only process ~100K tokens at once
- **Large files don't fit**: A 5000-line file might be too big
- **Better focus**: Smaller pieces = more relevant results

#### Intermediate: Chunking Strategies

| Strategy | How It Works | Pros | Cons |
|----------|--------------|------|------|
| **Fixed-size** | Split every N lines/tokens | Simple | May split mid-function |
| **Semantic** | Split at function/class boundaries | Clean boundaries | Needs code parsing(AST) |
| **Sliding window** | Overlapping chunks | Preserves context | Duplicates data |

#### Example: Fixed-size Chunking
```python
# Original: 900 tokens
def login(): ...      # 300 tokens
def logout(): ...     # 300 tokens  
def verify(): ...     # 300 tokens

# Chunk size: 400 tokens
# Result:
Chunk 1: def login() + part of logout()   # 400 tokens
Chunk 2: rest of logout() + def verify()  # 400 tokens
# Problem: logout() is split!
```

#### Example: Semantic Chunking
```python
# Same file, but split at function boundaries
Chunk 1: def login(): ...    # 300 tokens (complete)
Chunk 2: def logout(): ...   # 300 tokens (complete)
Chunk 3: def verify(): ...   # 300 tokens (complete)
# Better: Each function is intact
```

#### Advanced: When to Chunk
```
IF content_tokens > TOKEN_LIMIT:
    IF can_parse_code:
        Use semantic chunking (by function/class)
    ELSE:
        Use fixed-size with overlap
ELSE:
    Keep as single chunk
```

---

### 2. EMBEDDINGS

#### Basic: What is an Embedding?
An **embedding** is a way to convert text/code into a list of numbers that captures its **meaning**.

A specific type of vector that represents meaning

```
# This is a vector (just numbers)
coordinates = [3, 4, 5]

# This is ALSO a vector, but we call it an "embedding"
# because it represents the MEANING of code
embedding = [0.12, -0.45, 0.78, ...]
```

Think of it like GPS coordinates for words:
- "Paris" → [48.8, 2.3] (latitude, longitude)
- "London" → [51.5, -0.1]
- Cities close in meaning are close in coordinates

For code:
- `def login(user):` → [0.12, -0.45, 0.78, ...] (1536 numbers)
- `def authenticate(u):` → [0.14, -0.42, 0.80, ...] (similar numbers!)

#### Why Numbers?
Computers can't understand "meaning" directly. But they can:
- Compare numbers (is 0.12 close to 0.14? Yes!)
- Do math on numbers (find distance between two points)

#### Visual Example
```
                    Code Meaning Space
                          ↑
    [login code] ●────────┼─── Similar! ───● [auth code]
                          │
                          │
    [database code] ●─────┼───────────────● [query code]
                          │
    ←─────────────────────┼─────────────────────→
                          │
    [UI button] ●─────────┼───────────────● [UI form]
                          ↓

Similar code = Close points
Different code = Far apart points
```

#### Intermediate: How Embeddings Are Created

1. **Input**: Code or text
2. **Model**: Neural network (trained on millions of examples)
3. **Output**: Fixed-size vector (e.g., 1536 dimensions)

```python
# Using OpenAI
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    input="def login(user, password): ...",
    model="text-embedding-3-small"
)
embedding = response.data[0].embedding  # [0.12, -0.45, ...]
```

```python
# Using Sentence Transformers (free, local)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

embedding = model.encode("def login(user, password): ...")
# Returns: numpy array [0.12, -0.45, ...]
```

#### Advanced: Embedding Properties

| Property | Meaning |
|----------|---------|
| **Dimension** | Number of values (e.g., 1536) |
| **Magnitude** | Length of vector (usually normalized to 1) |
| **Direction** | Points toward "meaning" in high-dimensional space |

**Key Insight**: Similar meaning = Similar direction = High cosine similarity

---

### 3. VECTOR REPRESENTATION

#### Basic: What is a Vector?
A **vector** is just a list of numbers.
Any list of numbers [1, 2, 3]

```python
# 2D vector (like a point on a map)
position = [3, 4]  # x=3, y=4

# 3D vector (like a point in space)
position = [3, 4, 5]  # x=3, y=4, z=5

# Embedding vector (high-dimensional)
embedding = [0.12, -0.45, 0.78, 0.23, ...]  # 1536 numbers!
```

#### Why Vectors for Code?
- **Searchable**: Find similar vectors quickly
- **Mathematical**: Can measure distance/similarity
- **Compact**: Fixed size regardless of code length

```
"def authenticate_user(username, password): ..."  (50 characters)
                    ↓
            [0.12, -0.45, 0.78, ...]              (1536 numbers)

"def auth(u, p): check(u, p)"                     (28 characters)  
                    ↓
            [0.14, -0.42, 0.80, ...]              (1536 numbers)

Both become same-size vectors!
```

#### Intermediate: Vector Similarity (Cosine Similarity)

How do we know if two vectors are similar?

**Cosine Similarity** = Measure the angle between two vectors

```
                    ↑ Y-axis
                    │
         Vector A   │   
              ●     │      
             /      │     
            /       │    
           / θ      │   Vector B
          /         │  ●
         /__________│_/____________→ X-axis
       Origin      
       (0,0)

Both A and B start from origin (0,0) and point to their coordinates.
```
The Math:

```
import math

# Two 2D vectors (simple example)
A = [3, 4]    # Points to (3, 4)
B = [4, 3]    # Points to (4, 3)

# Step 1: Dot product (multiply matching elements, sum them)
dot_product = A[0]*B[0] + A[1]*B[1]  # 3*4 + 4*3 = 12 + 12 = 24

# Step 2: Magnitude (length) of each vector
magnitude_A = math.sqrt(A[0]**2 + A[1]**2)  # √(9+16) = √25 = 5
magnitude_B = math.sqrt(B[0]**2 + B[1]**2)  # √(16+9) = √25 = 5

# Step 3: Cosine of angle
cosine_theta = dot_product / (magnitude_A * magnitude_B)  # 24 / 25 = 0.96

# Step 4: Actual angle (if you want it)
angle_radians = math.acos(cosine_theta)  # 0.28 radians
angle_degrees = math.degrees(angle_radians)  # ~16 degrees
```

For similarity, we only need cosine (step 3):
cosine = 1.0 → vectors point same direction (identical)
cosine = 0.0 → vectors are perpendicular (unrelated)
cosine = -1.0 → vectors point opposite (opposite meaning)


**Formula** (simplified):
```
similarity = (A · B) / (|A| × |B|)

Where:
- A · B = sum of (a1×b1 + a2×b2 + ...)
- |A| = length of vector A
```

**Example**:
```python
import numpy as np

vec_login = [0.8, 0.6, 0.0]
vec_auth  = [0.7, 0.7, 0.1]
vec_database = [0.1, 0.2, 0.9]

# Cosine similarity
def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

cosine_sim(vec_login, vec_auth)      # 0.98 - Very similar!
cosine_sim(vec_login, vec_database)  # 0.28 - Not similar
```

#### Advanced: Why 1536 Dimensions?

- **2-3 dimensions**: Easy to visualize, but can't capture complex meaning
- **1536 dimensions**: Can represent nuanced differences in meaning
- It depends on the model you use.
```
Model	                                Dimensions
OpenAI text-embedding-3-small	          1536
OpenAI text-embedding-3-large	          3072
Sentence-Transformers all-MiniLM-L6-v2	   384
Cohere embed	                          1024
Google Gemini	                           768
```
- More dimensions = can capture more nuance = more accurate
- More dimensions = more storage = slower search
- It's a tradeoff chosen by model creators

```
2D: Can only distinguish "near" vs "far"
1536D: Can distinguish:
  - Authentication code vs Authorization code
  - Python login vs JavaScript login
  - Login with password vs Login with OAuth
  - ... and millions of other subtle differences
```

---

### Putting It All Together

```
┌─────────────────────────────────────────────────────────────────┐
│                         THE FLOW                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Large Code File                                               │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────┐                                                   │
│   │ CHUNKER │ ──→ Split into manageable pieces                  │
│   └─────────┘                                                   │
│        │                                                        │
│        ▼                                                        │
│   ┌──────────────┐                                              │
│   │ Chunk 1      │  "def login(): ..."                          │
│   │ Chunk 2      │  "def logout(): ..."                         │
│   │ Chunk 3      │  "class User: ..."                           │
│   └──────────────┘                                              │
│        │                                                        │
│        ▼                                                        │
│   ┌───────────────────┐                                         │
│   │ EMBEDDING MODEL   │ ──→ Convert each chunk to vector        │
│   └───────────────────┘                                         │
│        │                                                        │
│        ▼                                                        │
│   ┌──────────────────────────────────────┐                      │
│   │ VECTOR DATABASE                      │                      │
│   │                                      │                      │
│   │  Chunk 1 → [0.12, -0.45, 0.78, ...]  │                      │
│   │  Chunk 2 → [0.34, 0.21, -0.56, ...]  │                      │
│   │  Chunk 3 → [-0.11, 0.67, 0.44, ...]  │                      │
│   │                                      │                      │
│   └──────────────────────────────────────┘                      │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────┐                                           │
│   │ SIMILARITY      │ ──→ "Find code similar to this change"    │
│   │ SEARCH          │     Returns: Chunk 1 (most similar)       │
│   └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Quick Reference

| Concept | One-liner | Example |
|---------|-----------|---------|
| **Chunk** | Piece of code | `def login(): ...` |
| **Embedding** | Code → Numbers | `[0.12, -0.45, ...]` |
| **Vector** | List of numbers | `[0.12, -0.45, 0.78]` |
| **Cosine Similarity** | How similar are two vectors? | `0.98 = very similar` |

---

## Key Concepts Summary (Original)

### Tokenization
Breaking code/text into tokens for AI processing. Tokens are the basic units AI models understand.

### Vector Database
Database optimized for storing and querying vectors. Enables fast similarity search using mathematical operations.

### Semantic Search
Finding similar content based on meaning (semantics) rather than exact text matching. Uses vector similarity.

### RAG (Retrieval Augmented Generation)
Technique that retrieves relevant context first, then augments the prompt with that context before generating output.

### Prompt Engineering
Crafting effective prompts that guide AI to produce desired output. Includes templates, examples, and instructions.

### Context Window
Maximum number of tokens that can be sent to AI in one request. Managing this is crucial for large codebases.

---

## Implementation Order

1. **Phase 1-2**: Ingestion + Preprocessing (basic functionality)
2. **Phase 3**: Feature Extraction (tokenization, chunking)
3. **Phase 4-5**: Indexing + Retrieval (vector DB setup)
4. **Phase 6**: Generation (AI integration)
5. **Phase 7**: Post-Processing (file output, Confluence sync)

Each phase builds on the previous, allowing incremental learning and testing.