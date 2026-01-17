"""
Change Detector Module

LEARNING: Git commands and Python subprocess

What we're building:
- Detect if we're in a git repository
- Get remote tracking branch
- Get list of changed files
- Foundation for change analysis
"""

import logging
import subprocess
from pathlib import Path

from src.exceptions import GitNotInstalledError, InvalidRepositoryError

# Set up module logger
logger = logging.getLogger(__name__)


def is_git_repo(repo_path: str = ".") -> bool:
    """
    Check if the given path is a git repository.
    
    LEARNING POINT:
    - subprocess.run() executes shell commands
    - check=False means don't raise exception on error
    - returncode == 0 means command succeeded
    
    Args:
        repo_path: Path to check (default: current directory)
    
    Returns:
        True if it's a git repo, False otherwise
    
    Raises:
        GitNotInstalledError: If git is not installed on the system
        InvalidRepositoryError: If the path does not exist
    """
    # Path is a class in the pathlib module that represents a file system path
    # It provides methods to manipulate file system paths in a platform-independent way
    path = Path(repo_path)
    
    # Check if path exists first
    if not path.exists():
        logger.error("Path does not exist: %s", repo_path)
        raise InvalidRepositoryError(repo_path, reason="Path does not exist")
    
    logger.debug("Running command: git rev-parse --git-dir in %s", repo_path)
    
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        # returncode == 0 means the command succeeded (it's a git repo)
        if result.returncode == 0:
            logger.debug("Valid git repository: %s", repo_path)
            return True
        else:
            logger.debug("Not a git repository: %s", repo_path)
            return False
            
    except FileNotFoundError:
        # FileNotFoundError is raised ONLY when the 'git' executable is not found
        logger.error("Git is not installed on this system")
        raise GitNotInstalledError()


def get_remote_branch(repo_path: str = ".") -> str:
    """
    Get the remote tracking branch name (e.g., origin/main).
    
    LEARNING POINT:
    - git rev-parse --abbrev-ref --symbolic-full-name @{u}
    - @{u} is shorthand for "upstream" (the remote tracking branch)
    - Returns something like "origin/main" or "origin/master"
    
    Args:
        repo_path: Path to git repository
    
    Returns:
        Remote branch name (e.g., "origin/main")
        Falls back to "origin/main" if no upstream is set
    
    Raises:
        GitNotInstalledError: If git is not installed on the system
    """
    logger.debug("Running command: git rev-parse --abbrev-ref --symbolic-full-name @{u} in %s", repo_path)
    
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        remote = result.stdout.strip()
        logger.debug("Remote tracking branch: %s", remote)
        return remote
        
    except subprocess.CalledProcessError:
        # No upstream branch set, default to origin/main
        logger.warning("No upstream branch set, defaulting to origin/main")
        return "origin/main"
    except FileNotFoundError:
        logger.error("Git is not installed on this system")
        raise GitNotInstalledError()


def get_changed_files(base_ref: str = "HEAD~1", repo_path: str = ".") -> list[str]:
    """
    Get list of files that changed compared to a base reference.
    
    LEARNING POINT:
    - git diff --name-only shows only filenames (not full diff)
    - HEAD~1 means previous commit
    - check=True raises exception if command fails
    
    Args:
        base_ref: Git reference to compare against (default: previous commit)
        repo_path: Path to git repository
    
    Returns:
        List of changed file paths (empty list if no changes or error)
    
    Raises:
        GitNotInstalledError: If git is not installed on the system
        InvalidRepositoryError: If the path does not exist
    """
    if not is_git_repo(repo_path):
        logger.warning("Not a git repository, returning empty list: %s", repo_path)
        return []
    
    logger.debug("Running command: git diff --name-only %s in %s", base_ref, repo_path)
    
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Split by newline and filter empty strings
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        logger.info("Found %d changed file(s) in %s", len(files), repo_path)
        return files
        
    except subprocess.CalledProcessError as e:
        # Git command failed (maybe no commits yet, or invalid ref)
        logger.warning(
            "Git diff failed for ref '%s': %s", 
            base_ref, 
            e.stderr.strip() if e.stderr else "Unknown error"
        )
        return []
