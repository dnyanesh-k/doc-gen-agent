"""
Chunker Module

LEARNING: Splitting large content for LLM processing

What we're building:
- Check if content needs chunking
- Split content into smaller pieces
- Preserve code structure where possible

Key Concept:
- Large files don't fit in LLM context window
- We split them into chunks that DO fit
- Each chunk should be meaningful (not split mid-function)
"""

import logging
from typing import List

from src.feature_extraction.tokenizer import count_tokens, get_token_limit

# Set up module logger
logger = logging.getLogger(__name__)

# Default chunk settings
DEFAULT_CHUNK_SIZE = 2000  # tokens per chunk
DEFAULT_OVERLAP = 200      # overlap between chunks for context


def needs_chunking(content: str, limit: int = None) -> bool:
    """
    Check if content exceeds token limit and needs chunking.
    
    LEARNING POINT:
    - Simple threshold check
    - Use conservative limit to leave room for prompt + response
    
    Args:
        content: Text content to check
        limit: Token limit (default: from tokenizer)
    
    Returns:
        True if content needs chunking
    """
    if limit is None:
        limit = get_token_limit()
    
    token_count = count_tokens(content)
    needs_chunk = token_count > limit
    
    if needs_chunk:
        logger.info("Content needs chunking: %d tokens > %d limit", token_count, limit)
    
    return needs_chunk


def chunk_by_lines(content: str, chunk_size: int = DEFAULT_CHUNK_SIZE, 
                   overlap: int = DEFAULT_OVERLAP) -> List[dict]:
    """
    Split content into chunks by lines (simple approach).
    
    LEARNING POINT:
    - Split at line boundaries (not mid-line)
    - Add overlap so chunks have context from previous chunk
    - Each chunk is a dict with content and metadata
    
    Args:
        content: Text content to chunk
        chunk_size: Target tokens per chunk
        overlap: Tokens to overlap between chunks
    
    Returns:
        List of chunk dicts: [{'content': '...', 'tokens': N, 'index': 0}, ...]
    """
    if not content:
        return []
    
    # If content fits in one chunk, return as-is
    total_tokens = count_tokens(content)
    if total_tokens <= chunk_size:
        return [{
            'content': content,
            'tokens': total_tokens,
            'index': 0
        }]
    
    lines = content.split('\n')
    chunks = []
    current_chunk_lines = []
    current_tokens = 0
    
    for line in lines:
        line_tokens = count_tokens(line)
        
        # If adding this line exceeds chunk size, save current chunk
        if current_tokens + line_tokens > chunk_size and current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            chunks.append({
                'content': chunk_content,
                'tokens': current_tokens,
                'index': len(chunks)
            })
            
            # Keep some lines for overlap (context continuity)
            overlap_tokens = 0
            overlap_lines = []
            for prev_line in reversed(current_chunk_lines):
                prev_tokens = count_tokens(prev_line)
                if overlap_tokens + prev_tokens > overlap:
                    break
                overlap_lines.insert(0, prev_line)
                overlap_tokens += prev_tokens
            
            current_chunk_lines = overlap_lines
            current_tokens = overlap_tokens
        
        current_chunk_lines.append(line)
        current_tokens += line_tokens
    
    # Don't forget the last chunk
    if current_chunk_lines:
        chunk_content = '\n'.join(current_chunk_lines)
        chunks.append({
            'content': chunk_content,
            'tokens': count_tokens(chunk_content),
            'index': len(chunks)
        })
    
    logger.info("Split content into %d chunks", len(chunks))
    return chunks


def chunk_content(content: str, chunk_size: int = DEFAULT_CHUNK_SIZE,
                  overlap: int = DEFAULT_OVERLAP) -> List[dict]:
    """
    Main chunking function - splits content into manageable pieces.
    
    LEARNING POINT:
    - This is the main entry point for chunking
    - Currently uses line-based chunking (simple but effective)
    - Can be extended to use semantic chunking (AST-based) later
    
    Args:
        content: Text content to chunk
        chunk_size: Target tokens per chunk
        overlap: Tokens to overlap between chunks
    
    Returns:
        List of chunk dicts with content, tokens, and index
    """
    return chunk_by_lines(content, chunk_size, overlap)
