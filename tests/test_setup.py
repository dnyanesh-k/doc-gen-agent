#!/usr/bin/env python3
"""
Test script to verify installation and setup.
Run this after installing dependencies to check everything works.
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing Python package imports...")
    
    try:
        import yaml
        print("  ✅ pyyaml")
    except ImportError:
        print("  ❌ pyyaml - not installed")
        return False
    
    try:
        import psycopg2
        print("  ✅ psycopg2")
    except ImportError:
        print("  ❌ psycopg2 - not installed")
        return False
    
    try:
        from pgvector.psycopg2 import register_vector
        print("  ✅ pgvector")
    except ImportError:
        print("  ❌ pgvector - not installed")
        return False
    
    try:
        import tiktoken
        print("  ✅ tiktoken")
    except ImportError:
        print("  ❌ tiktoken - not installed")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv")
    except ImportError:
        print("  ❌ python-dotenv - not installed")
        return False
    
    # Optional: sentence-transformers
    try:
        import sentence_transformers
        print("  ✅ sentence-transformers (optional)")
    except ImportError:
        print("  ⚠️  sentence-transformers (optional - not needed until Phase 5)")
    
    return True

def test_env_file():
    """Test if .env file exists."""
    print("\nTesting .env file...")
    
    if os.path.exists('.env'):
        print("  ✅ .env file exists")
        return True
    else:
        print("  ⚠️  .env file not found")
        print("     Create it from .env.example if needed")
        return False

def test_database_connection():
    """Test PostgreSQL connection."""
    print("\nTesting database connection...")
    
    try:
        from dotenv import load_dotenv
        import psycopg2
        
        load_dotenv()
        
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB', 'docgen_vectors')
        )
        
        # Test pgvector extension
        cursor = conn.cursor()
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        result = cursor.fetchone()
        
        if result:
            print("  ✅ PostgreSQL connection successful")
            print("  ✅ pgvector extension enabled")
        else:
            print("  ⚠️  PostgreSQL connected but pgvector extension not enabled")
            print("     Run: CREATE EXTENSION vector; in your database")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"  ❌ Database connection failed: {e}")
        print("     Make sure:")
        print("     1. Docker container is running: docker-compose up -d")
        print("     2. .env file has correct credentials")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_docker_compose():
    """Check if docker-compose is available."""
    print("\nTesting Docker Compose...")
    
    import subprocess
    try:
        result = subprocess.run(
            ['docker-compose', 'ps'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if 'docgen-postgres' in result.stdout or 'postgres' in result.stdout.lower():
            print("  ✅ Docker Compose is running")
            print("  ✅ PostgreSQL container detected")
            return True
        else:
            print("  ⚠️  Docker Compose available but container not running")
            print("     Run: docker-compose up -d")
            return False
            
    except FileNotFoundError:
        print("  ⚠️  docker-compose not found")
        print("     Install Docker Compose or use 'docker compose' (newer syntax)")
        return False
    except Exception as e:
        print(f"  ⚠️  Could not check Docker: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Doc-Gen-Agent Setup Test")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Python Packages", test_imports()))
    
    # Test .env file
    results.append(("Environment File", test_env_file()))
    
    # Test Docker
    results.append(("Docker Compose", test_docker_compose()))
    
    # Test database
    results.append(("Database Connection", test_database_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Setup is complete.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
