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
"""
# On a different network (home WiFi, mobile hotspot):
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# This downloads the model to ~/.cache/huggingface/hub/
# After that, your code will work with embeddings!
"""

import logging
import os
from pathlib import Path
from typing import List

# Set up module logger
logger = logging.getLogger(__name__)

# Global model cache (avoid reloading)
_model_cache = {}

# Default model: fast and good quality, 384 dimensions
DEFAULT_MODEL = "all-MiniLM-L6-v2"

# Flag to track if model loading failed (network issues, etc.)
_model_load_failed = False
_model_status_logged = False

# Import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed - pip install sentence-transformers")


def _get_cache_path(model_name: str) -> Path:
    """Get the expected cache path for a model."""
    # Hugging Face cache location
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    # Model folder name format: models--org--model-name
    model_folder = f"models--sentence-transformers--{model_name}"
    return cache_dir / model_folder


def is_model_cached(model_name: str = DEFAULT_MODEL) -> bool:
    """
    Check if the model is already downloaded/cached locally.
    
    LEARNING POINT:
    - sentence-transformers caches models in ~/.cache/huggingface/hub/
    - We check if the folder exists to avoid network calls
    
    Args:
        model_name: Name of the model
    
    Returns:
        True if model is cached locally
    """
    cache_path = _get_cache_path(model_name)
    exists = cache_path.exists() and any(cache_path.iterdir()) if cache_path.exists() else False
    logger.debug("Model cache check: %s -> %s", model_name, "cached" if exists else "not cached")
    return exists


def is_embeddings_available() -> bool:
    """
    Check if embedding generation is available.
    
    Returns:
        True if sentence-transformers installed AND model is cached
    """
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return False
    if _model_load_failed:
        return False
    return is_model_cached(DEFAULT_MODEL)


def _get_model(model_name: str = DEFAULT_MODEL):
    """
    Get or load sentence-transformers model (cached).
    
    LEARNING POINT:
    - Models are large, loading takes time
    - We cache the model so it's only loaded once
    - Returns None if model can't be loaded (not cached or network issues)
    
    Args:
        model_name: Name of the model to load
    
    Returns:
        Loaded SentenceTransformer model or None if unavailable
    """
    global _model_load_failed, _model_status_logged
    
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        if not _model_status_logged:
            print("   ⚠️  sentence-transformers not installed. Run: pip install sentence-transformers")
            _model_status_logged = True
        return None
    
    if _model_load_failed:
        return None
    
    # Check if model is cached locally FIRST (avoid network calls)
    if not is_model_cached(model_name):
        if not _model_status_logged:
            print(f"   ⚠️  Embedding model not cached locally.")
            print(f"      To download, run on a network without proxy:")
            print(f"      python -c \"from sentence_transformers import SentenceTransformer; SentenceTransformer('{model_name}')\"")
            print(f"      Embeddings will be skipped for now.")
            _model_status_logged = True
        _model_load_failed = True
        return None
    
    if model_name not in _model_cache:
        logger.info("Loading model from cache: %s", model_name)
        try:
            # Load from local cache only (no network)
            _model_cache[model_name] = SentenceTransformer(model_name, local_files_only=True)
            print(f"   ✅ Embedding model loaded: {model_name}")
        except Exception as e:
            logger.error("Failed to load model %s: %s", model_name, str(e))
            if not _model_status_logged:
                print(f"   ⚠️  Failed to load embedding model: {str(e)}")
                _model_status_logged = True
            _model_load_failed = True
            return None
    
    return _model_cache[model_name]


def generate_embedding(text: str, model_name: str = DEFAULT_MODEL) -> List[float]:
    """
    Generate embedding for text.
    
    LEARNING POINT:
    - sentence-transformers runs locally, no API needed
    - Returns numpy array, we convert to list for storage
    - all-MiniLM-L6-v2 produces 384 dimensions
    - Returns empty list if model unavailable
    
    Args:
        text: Text to embed
        model_name: Model to use (default: all-MiniLM-L6-v2)
    
    Returns:
        List of floats (embedding vector), empty if model unavailable
    """
    if not text:
        return []
    
    model = _get_model(model_name)
    if model is None:
        return []
    
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
    - Returns empty lists if model unavailable
    
    Args:
        texts: List of texts to embed
        model_name: Model to use
    
    Returns:
        List of embedding vectors, empty lists if model unavailable
    """
    if not texts:
        return []
    
    model = _get_model(model_name)
    if model is None:
        # Return empty embeddings for each text
        return [[] for _ in texts]
    
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
