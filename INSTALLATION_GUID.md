# Installation Guide

## What is Docker Compose?

**Docker Compose** lets you run multiple containers (services) together with one command. For us, it runs PostgreSQL with pgvector pre-installed.

**Why use it?**
- No manual PostgreSQL installation
- pgvector already included
- Easy to start/stop
- Same setup on any machine

---

## Step 1: Install Docker & Docker Compose

### What this does:
Installs Docker (container runtime) and Docker Compose (orchestration tool).

### Ubuntu/Debian:
```bash
# Update package list
sudo apt update

# Install Docker
sudo apt install docker.io docker-compose

# Verify Installation:
docker --version        # Should show Docker version
docker-compose --version # Should show Compose version

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Log out and back in for group change to take effect
```

### What just happened?
- Docker is now running on your system
- You can run containers (isolated applications)
- Docker Compose can manage multiple containers

## Step 2: Create docker-compose.yml

### What this does:
Defines PostgreSQL service with pgvector in a configuration file.

Create file in project root:

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg14
    container_name: docgen-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-docgen_vectors}
    ports:
      - "${DB_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Explanation of each part:
`image: pgvector/pgvector:pg14`
- Uses pre-built image with PostgreSQL 14 + pgvector
- No manual compilation needed

`container_name: docgen-postgres`
- Names the container for easy reference

`environment:`
- Sets database credentials
- Creates database docgen_vectors automatically

`ports: "5432:5432"`
- Maps container port 5432 to host port 5432
- Allows connection from your machine

`volumes: postgres_data`
- Persists data in Docker volume
- Data survives container restarts

`healthcheck:`
- Checks if PostgreSQL is ready
- Used by docker-compose to know when service is up

## Step 3: Start PostgreSQL Container

### What this does:
Downloads image (if needed) and starts PostgreSQL container.

```bash
# Navigate to project directory
cd doc-gen-agent

# Start PostgreSQL
docker-compose up -d
```

### What happens:
1. Downloads `pgvector/pgvector:pg14` image (first time only)
2. Creates Docker volume for data
3. Starts PostgreSQL container in background (`-d` flag)
4. Creates database `docgen_vectors`
5. pgvector extension is already available

### Verify it's running:
```bash
# Check container status
docker-compose ps

# Should show:
# NAME              STATUS          PORTS
# docgen-postgres   Up (healthy)    0.0.0.0:5432->5432/tcp

# Check logs
docker-compose logs postgres
```

### What just happened?
- PostgreSQL is running in a container
- Accessible on `localhost:5432`
- Database `docgen_vectors` exists
- pgvector extension ready to use

## Step 4: Connect and Enable Extension

### What this does:
Connects to PostgreSQL and enables pgvector extension.

```bash
# Connect to PostgreSQL in container
docker-compose exec postgres psql -U postgres -d docgen_vectors
```

### In PostgreSQL prompt:
```sql
-- Enable pgvector extension
CREATE EXTENSION vector;

-- Verify it's installed
\dx

-- Should show:
-- Name   | Version | Schema | Description
-- -------+---------+--------+------------
-- vector | 0.8.1   | public | vector data type

-- Test vector type
SELECT '[1,2,3]'::vector;

-- Exit
\q
```

### What just happened?
- Enabled vector extension in database
- Can now store and query vectors
- Ready for embedding storage

## Step 5: Install Python Dependencies

### What this does:
Installs Python packages needed by the agent.

```bash
# Create virtual environment (isolates packages)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### What each package does:
`pyyaml:` Reads/writes YAML config files
`psycopg2-binary:` Connects to PostgreSQL from Python
`pgvector:` Python client for pgvector operations
`tiktoken:` Counts tokens in text (for AI context limits)
`sentence-transformers:` Generates embeddings from code/text

## Step 6: Configure Environment

### What this does:
Creates `.env` file with database credentials that both Docker Compose and Python will use.

### Create .env file:
```bash
# Copy example template
cp .env.example .env

# Edit .env with your database credentials
nano .env  # or use your editor
```

### .env file content:
```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=docgen123
POSTGRES_DB=docgen_vectors
DB_HOST=localhost
DB_PORT=5432
```

### Why localhost?
- Container exposes port 5432 to host
- localhost:5432 connects to container's PostgreSQL

## Step 7: Test Connection

### What this does:
Verifies Python can connect to PostgreSQL using credentials from `.env`.

```python
# Test connection using .env
python3 -c "
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    database=os.getenv('POSTGRES_DB')
)
print('✅ PostgreSQL connection successful!')
conn.close()
"
```

**Or use the test script** (recommended - tests everything):
```bash
python tests/test_setup.py
```

### What just happened?
- Python loaded credentials from `.env`
- Connected to containerized PostgreSQL
- Ready to store/query vectors

## Step 8: Verify Complete Setup

### What this does:
Runs comprehensive tests to verify all components are working correctly.

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Run test script
python tests/test_setup.py
```

### What it tests:
- ✅ Python package imports (pyyaml, psycopg2, pgvector, tiktoken, etc.)
- ✅ .env file exists and is configured
- ✅ Docker Compose is running
- ✅ PostgreSQL connection works
- ✅ pgvector extension is enabled

### Expected output:
```
============================================================
Doc-Gen-Agent Setup Test
============================================================
Testing Python package imports...
  ✅ pyyaml
  ✅ psycopg2
  ✅ pgvector
  ✅ tiktoken
  ✅ python-dotenv

Testing .env file...
  ✅ .env file exists

Testing Docker Compose...
  ✅ Docker Compose is running
  ✅ PostgreSQL container detected

Testing database connection...
  ✅ PostgreSQL connection successful
  ✅ pgvector extension enabled

============================================================
Test Summary
============================================================
✅ PASS - Python Packages
✅ PASS - Environment File
✅ PASS - Docker Compose
✅ PASS - Database Connection

🎉 All tests passed! Setup is complete.
```

### What just happened?
- All components verified and working
- Ready to start development
- If any test fails, check the error messages and fix issues

## Common Commands

### Start PostgreSQL:
```bash
docker-compose up -d
```

### Stop PostgreSQL:
```bash
docker-compose down
```

### View Logs:
```bash
docker-compose logs -f postgres
```

### Connect to Database:
```bash
docker-compose exec postgres psql -U postgres -d docgen_vectors
```

### Restart Container:
```bash
docker-compose restart postgres
```

### Remove Everything (clean slate):
```bash
docker-compose down -v  # Removes volumes too
```
