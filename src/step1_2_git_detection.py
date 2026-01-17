"""
Step 1.2: Git Change Detection

LEARNING: Git commands and Python subprocess

What we're doing:
- Detect files that changed in git
- Learn to run git commands from Python
- Handle git errors gracefully

Concept: Programmatic git interaction
"""

import subprocess
import sys
from pathlib import Path


def get_changed_files(base_ref: str = "HEAD~1") -> list[str]:
    """
    Get list of files that changed.
    
    LEARNING POINT:
    - subprocess.run() executes shell commands
    - capture_output=True captures stdout/stderr
    - text=True returns string instead of bytes
    - check=True raises exception on error
    
    Args:
        base_ref: Git reference to compare against (default: previous commit)
    
    Returns:
        List of changed file paths
    """
    try:
        # Run: git diff --name-only HEAD~1
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Split by newline and filter empty strings
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        return files
        
    except subprocess.CalledProcessError as e:
        # Not a git repo or other git error
        if "not a git repository" in e.stderr.lower():
            return []  # Return empty list, not an error
        print(f"Git error: {e.stderr}", file=sys.stderr)
        return []
    except FileNotFoundError:
        print("Error: git not found. Is git installed?", file=sys.stderr)
        return []


def main():
    """Test the git detection."""
    print("Step 1.2: Git Change Detection\n")
    print("=" * 50)
    
    # Get changed files
    changed_files = get_changed_files()
    
    if not changed_files:
        print("No changed files detected.")
        print("\n💡 Tip: Make some changes and commit, then run again!")
    else:
        print(f"Found {len(changed_files)} changed file(s):\n")
        for file in changed_files:
            print(f"  - {file}")
    
    print("\n" + "=" * 50)
    print("✅ Step 1.2 Complete!")
    print("\nWhat we learned:")
    print("  - How to run git commands from Python")
    print("  - How to handle subprocess errors")
    print("  - How to parse command output")


if __name__ == "__main__":
    main()
