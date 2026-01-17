"""
Custom exceptions for doc-gen-agent.

This module defines a hierarchy of exceptions used throughout the project.
All custom exceptions inherit from DocGenError for easy catching.
"""


class DocGenError(Exception):
    """Base exception for all doc-gen-agent errors."""
    pass


class GitError(DocGenError):
    """Base exception for git-related errors."""
    pass


class GitNotInstalledError(GitError):
    """
    Raised when git executable is not found on the system.
    
    User action: Install Git from https://git-scm.com/
    """
    def __init__(self, message: str = None):
        self.message = message or "Git is not installed. Please install Git from https://git-scm.com/"
        super().__init__(self.message)


class InvalidRepositoryError(GitError):
    """
    Raised when the provided path is not a valid git repository.
    
    This can happen when:
    - The path does not exist
    - The path exists but is not a git repository
    """
    def __init__(self, path: str, reason: str = None):
        self.path = path
        self.reason = reason or "Not a valid git repository"
        self.message = f"{self.reason}: {path}"
        super().__init__(self.message)


class AnalysisError(DocGenError):
    """Raised when code analysis fails."""
    pass


class PipelineError(DocGenError):
    """Raised when pipeline orchestration fails."""
    pass
