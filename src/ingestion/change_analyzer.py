"""
Change Analyzer Module (Pre-Push Hook Version)

LEARNING: Git diff parsing, analyzing changes for documentation

What we're building:
- Get files changed in commits ready to push
- Analyze change types (added, modified, deleted)
- Parse diff to get added/deleted lines
- Handle all edge cases for documentation generation
"""

import logging
import os
import subprocess

from src.exceptions import GitNotInstalledError
from src.ingestion.change_detector import is_git_repo

# Set up module logger
logger = logging.getLogger(__name__)


def get_commits_to_push(repo_path: str, remote_branch: str) -> list[str]:
    """
    Get list of commit hashes that will be pushed to remote.
    
    LEARNING POINT:
    - git log origin/main..HEAD shows commits not yet pushed
    - The ".." syntax means "commits reachable from HEAD but not from origin/main"
    - --format=%H returns only the full commit hash
    
    Args:
        repo_path: Path to git repository
        remote_branch: Remote branch name (e.g., "origin/main")
    
    Returns:
        List of commit hashes (newest first)
    """
    if not is_git_repo(repo_path):
        return []
    
    logger.debug("Running command: git log %s..HEAD --format=%%H in %s", remote_branch, repo_path)
    
    try:
        result = subprocess.run(
            ["git", "log", f"{remote_branch}..HEAD", "--format=%H"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        commits = [c.strip() for c in result.stdout.splitlines() if c.strip()]
        logger.info("Found %d commit(s) to push", len(commits))
        return commits
        
    except subprocess.CalledProcessError as e:
        logger.warning("Failed to get commits to push: %s", e.stderr.strip() if e.stderr else "Unknown error")
        return []


def get_changed_files_to_push(repo_path: str, remote_branch: str) -> list[str]:
    """
    Get files that have been changed in commits ready to push.
    
    LEARNING POINT:
    - git diff --name-only origin/main..HEAD
    - Shows all files changed between remote and local HEAD
    - Includes: added, modified, and deleted files
    
    Args:
        repo_path: Path to git repository
        remote_branch: Remote branch name (e.g., "origin/main")
    
    Returns:
        List of changed file paths (relative to repo root)
    """
    if not is_git_repo(repo_path):
        return []
    
    logger.debug("Running command: git diff --name-only %s..HEAD in %s", remote_branch, repo_path)
    
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{remote_branch}..HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        logger.info("Found %d changed file(s) to push", len(files))
        return files
        
    except subprocess.CalledProcessError as e:
        logger.warning("Failed to get changed files: %s", e.stderr.strip() if e.stderr else "Unknown error")
        return []


def get_file_change_type(file_path: str, repo_path: str, remote_branch: str) -> str:
    """
    Get the change type for a file (added, modified, deleted, renamed).
    
    LEARNING POINT:
    - git diff --name-status shows status code + filename
    - Status codes: A=Added, M=Modified, D=Deleted, R=Renamed, C=Copied
    - First character of output is the status code
    
    Args:
        file_path: Path to the file (relative to repo)
        repo_path: Path to git repository
        remote_branch: Remote branch name (e.g., "origin/main")
    
    Returns:
        Change type: 'added', 'modified', 'deleted', 'renamed', or 'unknown'
    """
    logger.debug("Running command: git diff --name-status %s..HEAD -- %s", remote_branch, file_path)
    
    try:
        result = subprocess.run(
            ["git", "diff", "--name-status", f"{remote_branch}..HEAD", "--", file_path],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        output = result.stdout.strip()
        if not output:
            logger.debug("No changes found for file: %s", file_path)
            return "unknown"
        
        # First character is the status code
        status_char = output[0]
        
        # Map git status codes to human-readable names
        status_map = {
            'A': 'added',
            'M': 'modified',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied'
        }
        
        change_type = status_map.get(status_char, 'unknown')
        logger.debug("File %s change type: %s", file_path, change_type)
        return change_type
        
    except subprocess.CalledProcessError:
        logger.warning("Failed to get change type for: %s", file_path)
        return "unknown"


def get_diff_stats(file_path: str, repo_path: str, remote_branch: str) -> dict:
    """
    Get diff statistics (lines added/deleted) for a file.
    
    LEARNING POINT:
    - git diff --numstat gives: added_lines  deleted_lines  filename
    - More reliable than parsing +/- symbols from diff output
    - Binary files show "-" instead of numbers
    
    Args:
        file_path: Path to the file (relative to repo)
        repo_path: Path to git repository
        remote_branch: Remote branch name (e.g., "origin/main")
    
    Returns:
        Dict with 'added' and 'deleted' line counts
        Example: {'added': 10, 'deleted': 5}
    """
    logger.debug("Running command: git diff --numstat %s..HEAD -- %s", remote_branch, file_path)
    
    try:
        result = subprocess.run(
            ["git", "diff", "--numstat", f"{remote_branch}..HEAD", "--", file_path],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        output = result.stdout.strip()
        if not output:
            return {'added': 0, 'deleted': 0}
        
        # Format: "added_lines\tdeleted_lines\tfilename"
        # Binary files show: "-\t-\tfilename"
        parts = output.split('\t')
        
        # Handle binary files (shown as "-")
        added = int(parts[0]) if parts[0] != '-' else 0
        deleted = int(parts[1]) if parts[1] != '-' else 0
        
        logger.debug("File %s: +%d -%d lines", file_path, added, deleted)
        return {'added': added, 'deleted': deleted}
        
    except (subprocess.CalledProcessError, IndexError, ValueError) as e:
        logger.warning("Failed to get diff stats for %s: %s", file_path, str(e))
        return {'added': 0, 'deleted': 0}


def get_file_diff(file_path: str, repo_path: str, remote_branch: str) -> str:
    """
    Get the full diff content for a file.
    
    LEARNING POINT:
    - git diff origin/main..HEAD -- file shows changes to be pushed
    - Output is in unified diff format
    - For new files, shows all lines as additions (+)
    - For deleted files, shows all lines as deletions (-)
    
    Args:
        file_path: Path to the file (relative to repo)
        repo_path: Path to git repository
        remote_branch: Remote branch name (e.g., "origin/main")
    
    Returns:
        Diff content as string (empty string if no diff)
    """
    logger.debug("Running command: git diff %s..HEAD -- %s", remote_branch, file_path)
    
    try:
        result = subprocess.run(
            ["git", "diff", f"{remote_branch}..HEAD", "--", file_path],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        diff = result.stdout
        logger.debug("Got diff for %s: %d lines", file_path, len(diff.splitlines()))
        return diff
        
    except subprocess.CalledProcessError as e:
        logger.warning("Failed to get diff for %s: %s", file_path, e.stderr.strip() if e.stderr else "Unknown error")
        return ""


def parse_diff(diff: str) -> dict:
    """
    Parse unified diff to extract added and deleted lines.
    
    LEARNING POINT:
    - Unified diff format:
      - Lines starting with "+" are additions (except "+++" header)
      - Lines starting with "-" are deletions (except "---" header)
      - Lines starting with "@@" are hunk headers (line numbers)
      - Lines starting with " " (space) are context lines
    
    Args:
        diff: Diff content in unified diff format
    
    Returns:
        Dict with 'added' and 'deleted' lists of line content
        Example: {'added': ['new line 1', 'new line 2'], 'deleted': ['old line']}
    """
    added = []
    deleted = []
    
    for line in diff.splitlines():
        # Skip diff headers
        # "+++" marks the new file in header
        # "---" marks the old file in header  
        # "@@" marks hunk headers with line numbers
        if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
            continue
        
        # Skip other header lines (diff --git, index, etc.)
        if line.startswith('diff ') or line.startswith('index '):
            continue
        
        # Parse actual changes
        if line.startswith('+'):
            # Remove the '+' prefix to get actual line content
            added.append(line[1:])
        elif line.startswith('-'):
            # Remove the '-' prefix to get actual line content
            deleted.append(line[1:])
        # Lines starting with space are context (unchanged) - we ignore them
    
    logger.debug("Parsed diff: %d added, %d deleted lines", len(added), len(deleted))
    return {'added': added, 'deleted': deleted}


def get_file_content(file_path: str, repo_path: str) -> str:
    """
    Read the current content of a file from the repository.
    
    LEARNING POINT:
    - For new files or when you need full content (not just diff)
    - Uses Python's built-in file reading
    - Handles encoding issues gracefully
    
    Args:
        file_path: Path to the file (relative to repo)
        repo_path: Path to git repository
    
    Returns:
        File content as string (empty string if file doesn't exist or can't be read)
    """
    full_path = os.path.join(repo_path, file_path)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.debug("Read file %s: %d characters", file_path, len(content))
            return content
    except FileNotFoundError:
        logger.warning("File not found: %s", full_path)
        return ""
    except UnicodeDecodeError:
        logger.warning("Cannot read binary file: %s", file_path)
        return ""
    except IOError as e:
        logger.error("Error reading file %s: %s", file_path, str(e))
        return ""


def analyze_changes_for_docs(repo_path: str, remote_branch: str) -> list[dict]:
    """
    Analyze all changes and prepare data for documentation generation.
    
    LEARNING POINT:
    - Combines all analysis functions into one comprehensive result
    - Returns structured data ready for doc generation
    - Handles all change types appropriately
    - remote_branch is passed once from orchestrator (DRY principle)
    
    Args:
        repo_path: Path to git repository
        remote_branch: Remote branch name (e.g., "origin/main")
    
    Returns:
        List of dicts, each containing:
        - file_path: Path to the file
        - change_type: 'added', 'modified', 'deleted'
        - stats: {'added': N, 'deleted': N}
        - diff: Full diff content
        - parsed_diff: {'added': [...], 'deleted': [...]}
        - content: Full file content (for added/modified files)
    """
    if not is_git_repo(repo_path):
        logger.error("Not a git repository: %s", repo_path)
        return []
    
    changed_files = get_changed_files_to_push(repo_path, remote_branch)
    
    if not changed_files:
        logger.info("No files to analyze")
        return []
    
    results = []
    
    for file_path in changed_files:
        change_type = get_file_change_type(file_path, repo_path, remote_branch)
        stats = get_diff_stats(file_path, repo_path, remote_branch)
        diff = get_file_diff(file_path, repo_path, remote_branch)
        parsed_diff = parse_diff(diff)
        
        # Get file content for added/modified files (not deleted)
        content = ""
        if change_type != 'deleted':
            content = get_file_content(file_path, repo_path)
        
        results.append({
            'file_path': file_path,
            'change_type': change_type,
            'stats': stats,
            'diff': diff,
            'parsed_diff': parsed_diff,
            'content': content
        })
        
        logger.info(
            "Analyzed %s: %s (+%d/-%d lines)",
            file_path, change_type, stats['added'], stats['deleted']
        )
    
    return results
