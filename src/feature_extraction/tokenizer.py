"""
Tokenizer Module

LEARNING: Token counting for LLM context window management

What we're building:
- Count tokens in text using tiktoken
- Know if content fits in LLM context window
- Foundation for chunking decisions

Key Concept:
- Tokens are not words! "hello" = 1 token, "authentication" = 2-3 tokens
- Different models have different token limits
- We count tokens BEFORE sending to LLM to avoid errors
"""

import logging

# Set up module logger
logger = logging.getLogger(__name__)

# Try to import tiktoken, fall back to estimation
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
    logger.info("tiktoken available - using accurate token counting")
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not installed, using approximate token counting")

# Token limits for different models (leave room for response)
TOKEN_LIMITS = {
    'gpt-4': 8000,
    'gpt-4-turbo': 120000,
    'claude-3': 180000,
    'default': 4000  # Conservative default
}

# Fallback: average characters per token
CHARS_PER_TOKEN = 4


def count_tokens(text: str, model: str = "default") -> int:
    """
    Count tokens in text.
    
    LEARNING POINT:
    - tiktoken is OpenAI's tokenizer library
    - cl100k_base encoding works for GPT-4 and approximates Claude
    - Falls back to character estimation if tiktoken unavailable
    
    Args:
        text: Text to count tokens for
        model: Model name (for future model-specific counting)
    
    Returns:
        Number of tokens
    """
    if not text:
        return 0
    
    if TIKTOKEN_AVAILABLE:
        try:
            # cl100k_base works for GPT-4, good approximation for Claude
            encoder = tiktoken.get_encoding("cl100k_base")
            token_count = len(encoder.encode(text))
            logger.debug("Counted %d tokens (tiktoken)", token_count)
            return token_count
        except Exception as e:
            logger.warning("tiktoken failed: %s, using fallback", str(e))
    
    # Fallback: rough estimation
    # Code has more tokens per character due to symbols
    token_count = len(text) // CHARS_PER_TOKEN
    logger.debug("Estimated %d tokens (fallback)", token_count)
    return token_count


def get_token_limit(model: str = "default") -> int:
    """
    Get token limit for a model.
    
    LEARNING POINT:
    - Different models have different context windows
    - We use conservative limits to leave room for response
    
    Args:
        model: Model name
    
    Returns:
        Token limit for the model
    """
    return TOKEN_LIMITS.get(model, TOKEN_LIMITS['default'])


def estimate_chunks_needed(text: str, chunk_size: int = 2000) -> int:
    """
    Estimate how many chunks will be needed.
    
    Args:
        text: Text to chunk
        chunk_size: Target tokens per chunk
    
    Returns:
        Estimated number of chunks
    """
    total_tokens = count_tokens(text)
    if total_tokens <= chunk_size:
        return 1
    return (total_tokens // chunk_size) + 1
