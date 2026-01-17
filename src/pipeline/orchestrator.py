"""
Pipeline Orchestrator

LEARNING: Pipeline pattern, service orchestration

What this does:
- Orchestrates the entire documentation generation pipeline
- Manages flow between different stages
- Calls get_remote_branch() ONCE and passes to all functions (DRY principle)
"""

import logging
import sys
from typing import List, Dict
from pathlib import Path

from src.exceptions import GitNotInstalledError, InvalidRepositoryError
from src.ingestion.change_detector import is_git_repo, get_remote_branch
from src.ingestion.change_analyzer import (
    get_commits_to_push,
    get_changed_files_to_push,
    analyze_changes_for_docs
)

# Set up module logger
logger = logging.getLogger(__name__)


class DocGenPipeline:
    """
    Main pipeline orchestrator for documentation generation.
    
    LEARNING POINT:
    - Orchestrator pattern: coordinates multiple services
    - Single responsibility: manages flow, not business logic
    - DRY principle: get_remote_branch() called once in __init__
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
            'status': 'in_progress'
        }
        
        try:
            # Step 0: Validate repository
            print("\n[0/7] Validating repository...")
            if not is_git_repo(self.repo_path):
                print("   ❌ Not a git repository")
                results['status'] = 'not_a_repo'
                return results
            print("   ✅ Valid git repository")
            
            # Step 1: Get remote branch (ONCE - DRY principle)
            print("\n[1/7] Getting remote branch...")
            self.remote_branch = get_remote_branch(self.repo_path)
            results['remote_branch'] = self.remote_branch
            print(f"   ✅ Remote branch: {self.remote_branch}")
            
            # Step 2: Check commits to push
            print("\n[2/7] Checking commits to push...")
            commits = get_commits_to_push(self.repo_path, self.remote_branch)
            results['commits_to_push'] = commits
            
            if not commits:
                print("   ⚠️  No commits to push - already up to date")
                results['status'] = 'no_changes'
                return results
            print(f"   ✅ Found {len(commits)} commit(s) to push")
            
            # Step 3: Get changed files
            print("\n[3/7] Getting changed files...")
            changed_files = get_changed_files_to_push(self.repo_path, self.remote_branch)
            results['changed_files'] = changed_files
            
            if not changed_files:
                print("   ⚠️  No file changes detected")
                results['status'] = 'no_changes'
                return results
            print(f"   ✅ Found {len(changed_files)} changed file(s)")
            
            # Step 4: Analyze changes
            print("\n[4/7] Analyzing changes...")
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
                print(f"      {change['diff']}")
            
            if len(changes) > 5:
                print(f"CHANGES: {changes}")
                print(f"      ... and {len(changes) - 5} more")
            
            # Step 5: Feature extraction (future)
            print("\n[5/7] Feature Extraction: Generating embeddings...")
            print("   ⏳ Not implemented yet")
            
            # Step 6: Generation (future)
            print("\n[6/7] Generation: Creating documentation...")
            print("   ⏳ Not implemented yet")
            
            # Step 7: Post-processing (future)
            print("\n[7/7] Post-processing: Saving files...")
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
