"""
Pipeline Orchestrator

LEARNING: Pipeline pattern, service orchestration

What this does:
- Orchestrates the entire documentation generation pipeline
- Manages flow between different stages
- Calls get_remote_branch() ONCE and passes to all functions (DRY principle)
"""

import logging
from typing import Dict
from pathlib import Path

from src.exceptions import GitNotInstalledError, InvalidRepositoryError
from src.ingestion import is_git_repo, get_remote_branch, get_commits_to_push, get_changed_files_to_push, analyze_changes_for_docs
from src.feature_extraction import count_tokens, chunk_content, needs_chunking, generate_embedding, generate_embeddings_batch

# Set up module logger
logger = logging.getLogger(__name__)


class DocGenPipeline:
    """
    Main pipeline orchestrator for documentation generation.
    
    LEARNING POINT:
    - Orchestrator pattern: coordinates multiple services
    - Single responsibility: manages flow, not business logic
    - DRY principle: get_remote_branch() called once in __init__
    
    Pipeline stages:
    1. Ingestion - Detect and analyze code changes
    2. Feature Extraction - Tokenize, chunk, generate embeddings
    3. Indexing - Store embeddings in vector DB
    4. Retrieval - Semantic search for similar code
    5. Generation - Build prompts, send to LLM
    6. Post-processing - Save documentation
    """
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize the pipeline.
        
        Args:
            repo_path: Path to the git repository to analyze
        
        Raises:
            GitNotInstalledError: If git is not installed
            InvalidRepositoryError: If path is not a valid git repo
        """
        self.repo_path = str(Path(repo_path).resolve())
        self.remote_branch = None  # Will be set in run() after validation
        
        logger.info("Pipeline initialized for repo: %s", self.repo_path)
        
    def run(self) -> Dict:
        """
        Execute the complete pipeline.
        
        LEARNING POINT:
        - This method shows the entire flow
        - Each step is clear and sequential
        - remote_branch fetched ONCE and passed to all functions
        
        Returns:
            Dictionary with pipeline results
        """
        print("=" * 60)
        print("Doc-Gen-Agent Pipeline")
        print("=" * 60)
        
        results = {
            'repo_path': self.repo_path,
            'remote_branch': None,
            'commits_to_push': [],
            'changed_files': [],
            'changes': [],
            'features': [],  # Feature extraction results
            'status': 'in_progress'
        }
        
        try:
            # ============== STAGE 1: INGESTION ==============
            
            # Step 1.1: Validate repository
            print("\n[1/6] Ingestion: Validating repository...")
            if not is_git_repo(self.repo_path):
                print("   ❌ Not a git repository")
                results['status'] = 'not_a_repo'
                return results
            print("   ✅ Valid git repository")
            
            # Step 1.2: Get remote branch (ONCE - DRY principle)
            self.remote_branch = get_remote_branch(self.repo_path)
            results['remote_branch'] = self.remote_branch
            print(f"   ✅ Remote branch: {self.remote_branch}")
            
            # Step 1.3: Check commits to push
            commits = get_commits_to_push(self.repo_path, self.remote_branch)
            results['commits_to_push'] = commits
            
            if not commits:
                print("   ⚠️  No commits to push - already up to date")
                results['status'] = 'no_changes'
                return results
            print(f"   ✅ Found {len(commits)} commit(s) to push")
            
            # Step 1.4: Get changed files
            changed_files = get_changed_files_to_push(self.repo_path, self.remote_branch)
            results['changed_files'] = changed_files
            
            if not changed_files:
                print("   ⚠️  No file changes detected")
                results['status'] = 'no_changes'
                return results
            print(f"   ✅ Found {len(changed_files)} changed file(s)")
            
            # Step 1.5: Analyze changes
            changes = analyze_changes_for_docs(self.repo_path, self.remote_branch)
            results['changes'] = changes
            print(f"   ✅ Analyzed {len(changes)} file(s)")
            
            # Display change summary
            for change in changes[:5]:
                emoji = {
                    'added': '🆕',
                    'modified': '📝', 
                    'deleted': '🗑️',
                    'renamed': '📛'
                }.get(change['change_type'], '❓')
                print(f"      {emoji} {change['file_path']} (+{change['stats']['added']}/-{change['stats']['deleted']})")
            
            if len(changes) > 5:
                print(f"      ... and {len(changes) - 5} more")
            
            # ============== STAGE 2: FEATURE EXTRACTION ==============
            print("\n[2/6] Feature Extraction: Tokenize, chunk & embed...")
            
            # Trust git workflow - files in diff are already filtered by .gitignore
            # Binary files will have empty content (UnicodeDecodeError handled in get_file_content)
            
            features = []
            total_tokens = 0
            chunked_count = 0
            skipped_count = 0
            total_embeddings = 0
            
            for change in changes:
                file_path = change['file_path']
                content = change.get('content', '')
                diff = change.get('diff', '')
                
                # For deleted files, use deleted lines from parsed_diff
                if not content and change['change_type'] == 'deleted':
                    content = "\n".join(change.get('parsed_diff', {}).get('deleted', []))
                
                # Skip if content is empty (binary files, unreadable, etc.)
                if not content:
                    logger.debug("Skipping empty content: %s", file_path)
                    skipped_count += 1
                    continue
                
                # Count tokens
                content_tokens = count_tokens(content)
                diff_tokens = count_tokens(diff)
                total_tokens += content_tokens
                
                # Check if chunking needed and create chunks
                chunks = []
                if needs_chunking(content):
                    chunks = chunk_content(content)
                    chunked_count += 1
                else:
                    # Single chunk (whole content)
                    chunks = [{'content': content, 'tokens': content_tokens, 'index': 0}]
                
                # Generate embeddings for each chunk
                print(f"      🔄 Embedding {file_path}...", end=" ")
                chunk_contents = [chunk['content'] for chunk in chunks]
                
                try:
                    # Batch embedding is more efficient
                    embeddings = generate_embeddings_batch(chunk_contents)
                    
                    # Add embedding to each chunk
                    for i, chunk in enumerate(chunks):
                        chunk['embedding'] = embeddings[i] if i < len(embeddings) else []
                    
                    total_embeddings += len(embeddings)
                    print(f"✅ ({len(chunks)} chunks)")
                    
                except Exception as e:
                    logger.error("Embedding failed for %s: %s", file_path, str(e))
                    print(f"❌ Error: {str(e)}")
                    # Continue without embeddings
                    for chunk in chunks:
                        chunk['embedding'] = []
                
                # Generate embedding for diff (for searching by changes)
                diff_embedding = []
                if diff:
                    try:
                        diff_embedding = generate_embedding(diff)
                    except Exception as e:
                        logger.warning("Diff embedding failed for %s: %s", file_path, str(e))
                
                feature = {
                    'file_path': file_path,
                    'change_type': change['change_type'],
                    'content_tokens': content_tokens,
                    'diff_tokens': diff_tokens,
                    'chunks': chunks,
                    'diff': diff,
                    'diff_embedding': diff_embedding
                }
                features.append(feature)
            
            results['features'] = features
            
            print(f"\n   ✅ Feature extraction complete:")
            print(f"      Files processed: {len(features)}")
            print(f"      Files skipped (empty/unreadable): {skipped_count}")
            print(f"      Total tokens: {total_tokens}")
            print(f"      Total embeddings: {total_embeddings}")
            if chunked_count > 0:
                print(f"      Files chunked: {chunked_count}")
            
            # Summary of processed files
            print(f"\n   📊 Processed files:")
            for f in features[:5]:
                chunk_info = f"({len(f['chunks'])} chunks)" if len(f['chunks']) > 1 else ""
                has_embedding = "✅" if f['chunks'] and f['chunks'][0].get('embedding') else "❌"
                print(f"      {has_embedding} {f['file_path']}: {f['content_tokens']} tokens {chunk_info}")
            
            if len(features) > 5:
                print(f"      ... and {len(features) - 5} more")
            
            # ============== STAGE 3: INDEXING ==============
            print("\n[3/6] Indexing: Store embeddings...")
            print("   ⏳ Not implemented yet")
            
            # ============== STAGE 4: RETRIEVAL ==============
            print("\n[4/6] Retrieval: Semantic search...")
            print("   ⏳ Not implemented yet")
            
            # ============== STAGE 5: GENERATION ==============
            print("\n[5/6] Generation: Create documentation...")
            print("   ⏳ Not implemented yet")
            
            # ============== STAGE 6: POST-PROCESSING ==============
            print("\n[6/6] Post-processing: Save documentation...")
            print("   ⏳ Not implemented yet")
            
            results['status'] = 'complete'
            
        except GitNotInstalledError as e:
            print(f"\n   ❌ {e.message}")
            results['status'] = 'error'
            results['error'] = str(e.message)
            
        except InvalidRepositoryError as e:
            print(f"\n   ❌ {e.message}")
            results['status'] = 'error'
            results['error'] = str(e.message)
            
        except Exception as e:
            logger.exception("Pipeline error")
            print(f"\n   ❌ Unexpected error: {str(e)}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        print("\n" + "=" * 60)
        print(f"Pipeline execution: {results['status']}")
        print("=" * 60)
        
        return results
