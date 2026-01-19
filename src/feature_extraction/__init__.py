"""
Feature Extraction Module

Components:
- tokenizer: Count tokens for context window management
- chunker: Split large content into manageable pieces
- embeddings: Generate vector embeddings for semantic search
"""

from src.feature_extraction.tokenizer import count_tokens, get_token_limit
from src.feature_extraction.chunker import chunk_content, needs_chunking
from src.feature_extraction.embeddings import generate_embedding, generate_embeddings_batch, get_embedding_dimensions

__all__ = [
    'count_tokens',
    'get_token_limit',
    'chunk_content',
    'needs_chunking',
    'generate_embedding',
    'generate_embeddings_batch',
    'get_embedding_dimensions'
]
