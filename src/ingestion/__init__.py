"""Ingestion module - detects and analyzes code changes."""

from src.ingestion.change_detector import is_git_repo, get_remote_branch
from src.ingestion.change_analyzer import get_commits_to_push, get_changed_files_to_push, analyze_changes_for_docs

# Export the function
__all__ = ['is_git_repo', 'get_remote_branch', 'get_commits_to_push', 'get_changed_files_to_push', 'analyze_changes_for_docs']