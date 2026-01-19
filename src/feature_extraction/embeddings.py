"""
Embeddings Module

LEARNING: Converting text to vectors for semantic search

What we're building:
- Generate embeddings (vectors) from text/code
- Use sentence-transformers (free, local)
- Foundation for similarity search in RAG

Key Concept:
- Embedding = list of numbers representing meaning
- Similar text → similar numbers → close in vector space
- We use these to find "similar code" in our database
"""

import logging
from typing import List

# Set up module logger
logger = logging.getLogger(__name__)

# Import sentence-transformers
from sentence_transformers import SentenceTransformer

# Global model cache (avoid reloading)
_model_cache = {}

# Default model: fast and good quality, 384 dimensions
DEFAULT_MODEL = "all-MiniLM-L6-v2"


def _get_model(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
    """
    Get or load sentence-transformers model (cached).
    
    LEARNING POINT:
    - Models are large, loading takes time
    - We cache the model so it's only loaded once
    - all-MiniLM-L6-v2 is fast and good quality
    
    Args:
        model_name: Name of the model to load
    
    Returns:
        Loaded SentenceTransformer model
    """
    if model_name not in _model_cache:
        logger.info("Loading model: %s", model_name)
        _model_cache[model_name] = SentenceTransformer(model_name)
    return _model_cache[model_name]


def generate_embedding(text: str, model_name: str = DEFAULT_MODEL) -> List[float]:
    """
    Generate embedding for text.
    
    LEARNING POINT:
    - sentence-transformers runs locally, no API needed
    - Returns numpy array, we convert to list for storage
    - all-MiniLM-L6-v2 produces 384 dimensions
    
    Args:
        text: Text to embed
        model_name: Model to use (default: all-MiniLM-L6-v2)
    
    Returns:
        List of floats (embedding vector)
    """
    if not text:
        return []
    
    model = _get_model(model_name)
    embedding = model.encode(text)
    
    # Convert numpy array to list for JSON/DB storage
    embedding_list = embedding.tolist()
    logger.debug("Generated embedding: %d dimensions", len(embedding_list))
    
    return embedding_list


def generate_embeddings_batch(texts: List[str], model_name: str = DEFAULT_MODEL) -> List[List[float]]:
    """
    Generate embeddings for multiple texts (batch processing).
    
    LEARNING POINT:
    - Batch processing is more efficient than one-by-one
    - sentence-transformers handles batches natively
    - Uses GPU if available for faster processing
    
    Args:
        texts: List of texts to embed
        model_name: Model to use
    
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    model = _get_model(model_name)
    embeddings = model.encode(texts)
    
    # Convert numpy arrays to lists
    embeddings_list = [emb.tolist() for emb in embeddings]
    logger.info("Generated %d embeddings", len(embeddings_list))
    
    return embeddings_list


def get_embedding_dimensions(model_name: str = DEFAULT_MODEL) -> int:
    """
    Get the number of dimensions for the embedding model.
    
    LEARNING POINT:
    - Different models produce different dimensions
    - We need to know this for database schema (vector column size)
    - all-MiniLM-L6-v2 = 384 dimensions
    
    Args:
        model_name: Model name
    
    Returns:
        Number of dimensions
    """
    dimensions = {
        'all-MiniLM-L6-v2': 384,
        'all-mpnet-base-v2': 768,
        'paraphrase-MiniLM-L6-v2': 384,
    }
    return dimensions.get(model_name, 384)
