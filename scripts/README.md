# Qdrant Knowledge Management Scripts

Utility scripts for managing the Qdrant knowledge base collections.

## Available Scripts

### create_collections.py

Creates and manages the Qdrant collections for knowledge management.

**Collections (configurable via .env):**
- Knowledge collection - Project-specific institutional memory (7 types)
- Best practices collection - Agent-discovered best practices (1 type)

**Usage:**

```bash
# Check existing collections
python3 scripts/create_collections.py --check-only

# Create collections (if they don't exist)
python3 scripts/create_collections.py
```

### qdrant_cleanup.py

Safely audits and cleans up collections by removing duplicates, invalid entries, or test data.

**Usage:**

```bash
# Audit collections (safe, no changes)
python3 scripts/qdrant_cleanup.py --audit

# Show what would be deleted
python3 scripts/qdrant_cleanup.py --delete --dry-run

# Execute deletion (with confirmation)
python3 scripts/qdrant_cleanup.py --delete --execute

# Only delete test entries
python3 scripts/qdrant_cleanup.py --delete --test-only --execute

# Backup a collection
python3 scripts/qdrant_cleanup.py --backup bmad-knowledge
```

### populate_knowledge_base_optimized.py

Bulk population script that processes example population scripts with deduplication.

**Usage:**

```bash
python3 scripts/populate_knowledge_base_optimized.py
```

### run.sh

Wrapper script that loads `.env` and runs other scripts.

**Usage:**

```bash
./scripts/run.sh create_collections.py --check-only
./scripts/run.sh qdrant_cleanup.py --audit
```

## Configuration

All scripts use the centralized `config.py` module. Configuration is loaded from environment variables or `.env` file.

**Key environment variables:**
- `QDRANT_URL` - Qdrant server URL (default: `http://localhost:6333`)
- `QDRANT_API_KEY` - API key (optional for local)
- `QDRANT_KNOWLEDGE_COLLECTION` - Main collection name
- `QDRANT_BEST_PRACTICES_COLLECTION` - Best practices collection name

See `.env.example` for all options.

## Requirements

- Python 3.8+
- qdrant-client library (`pip install qdrant-client`)
- Qdrant server running

## Collection Details

### Knowledge Collection

**Purpose:** Project-specific institutional memory

**Types (7):**
1. `architecture_decision` - Major design choices and constraints
2. `agent_spec` - Agent capabilities and integration patterns
3. `story_outcome` - Completed story implementations
4. `error_pattern` - Common errors and solutions
5. `database_schema` - Table structures and constraints
6. `config_pattern` - Configuration examples
7. `integration_example` - Working integration code

### Best Practices Collection

**Purpose:** Agent-discovered universal best practices

**Types (1):**
1. `best_practice` - Performance, security, scalability patterns

### Common Settings

- **Vector Size:** 384 (default, configurable)
- **Distance Metric:** Cosine
- **Embedding Model:** sentence-transformers/all-MiniLM-L6-v2 (default, configurable)
