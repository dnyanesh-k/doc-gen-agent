#!/usr/bin/env python3
"""
Doc-Gen-Agent Main Entry Point

LEARNING: Entry point pattern, CLI structure

What this does:
- Thin entry point
- Sets up logging
- Parses command-line arguments
- Delegates to orchestrator
"""

import sys
import logging
import argparse
from pathlib import Path

from src.pipeline import DocGenPipeline


def setup_logging(debug: bool = False):
    """
    Configure logging for the application.
    
    LEARNING POINT:
    - Logging is configured once at entry point
    - All modules use logging.getLogger(__name__)
    - Debug mode shows more details
    """
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(levelname)s - %(name)s - %(message)s"
    )


def main():
    """
    Main entry point for the doc-gen-agent.
    
    LEARNING POINT:
    - Entry point should be thin
    - Parse arguments, setup logging, create pipeline, run it
    - All business logic in orchestrator/services
    """
    parser = argparse.ArgumentParser(
        description="AI-powered documentation generator"
    )
    parser.add_argument(
        '--repo',
        type=str,
        default='/home/dnyaneshwar/project/system-design',
        help='Path to git repository'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(debug=args.debug)
    
    # Create and run pipeline
    pipeline = DocGenPipeline(repo_path=args.repo)
    results = pipeline.run()
    
    # Print summary
    print("\n📊 Results Summary:")
    print(f"   Repository: {results['repo_path']}")
    print(f"   Remote branch: {results['remote_branch']}")
    print(f"   Commits to push: {len(results['commits_to_push'])}")
    print(f"   Files changed: {len(results['changed_files'])}")
    print(f"   Status: {results['status']}")
    
    # Exit with appropriate code
    if results['status'] in ('no_changes', 'complete'):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
