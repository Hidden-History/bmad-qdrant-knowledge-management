# Configuration Guide

> All configuration options for Qdrant MCP Knowledge Management

## TL;DR

Copy `.env.example` to `.env` and edit. Most defaults work out of the box for local development.

## Environment Variables

All configuration is loaded from environment variables. You can set these in a `.env` file or export them directly.

### Required Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_API_KEY` | (empty) | API key for Qdrant Cloud |
| `QDRANT_KNOWLEDGE_COLLECTION` | `bmad-knowledge` | Main knowledge collection name |
| `QDRANT_BEST_PRACTICES_COLLECTION` | `bmad-best-practices` | Best practices collection name |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model name |
| `EMBEDDING_DIMENSION` | `384` | Vector dimension (must match model) |
| `PROJECT_NAME` | `bmad-project` | Project name for metadata |
| `MIN_CONTENT_LENGTH` | `100` | Minimum content length for entries |
| `MAX_CONTENT_LENGTH` | `50000` | Maximum content length for entries |
| `SIMILARITY_THRESHOLD` | `0.85` | Threshold for duplicate detection |

## Configuration Examples

### Local Development

```bash
# .env
QDRANT_URL=http://localhost:6333
QDRANT_KNOWLEDGE_COLLECTION=bmad-knowledge
QDRANT_BEST_PRACTICES_COLLECTION=bmad-best-practices
PROJECT_NAME=my-project
```

### Qdrant Cloud

```bash
# .env
QDRANT_URL=https://abc123-xyz.us-east4-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=your-api-key-here
QDRANT_KNOWLEDGE_COLLECTION=my-project-knowledge
QDRANT_BEST_PRACTICES_COLLECTION=my-project-best-practices
PROJECT_NAME=my-project
```

### Custom Embedding Model

```bash
# .env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
EMBEDDING_DIMENSION=768
```

Common embedding models and dimensions:
- `all-MiniLM-L6-v2`: 384 dimensions (default, good balance)
- `all-mpnet-base-v2`: 768 dimensions (higher quality)
- `text-embedding-ada-002`: 1536 dimensions (OpenAI)

## Claude MCP Configuration

### Basic Configuration

Add to your Claude settings:

```json
{
  "mcpServers": {
    "qdrant": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-qdrant"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "bmad-knowledge"
      }
    }
  }
}
```

### Dual Collection Configuration

For using both knowledge and best-practices collections:

```json
{
  "mcpServers": {
    "qdrant-knowledge": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-qdrant"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "bmad-knowledge"
      }
    },
    "qdrant-best-practices": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-qdrant"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "bmad-best-practices"
      }
    }
  }
}
```

### With API Key (Qdrant Cloud)

```json
{
  "mcpServers": {
    "qdrant": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-qdrant"],
      "env": {
        "QDRANT_URL": "https://your-cluster.cloud.qdrant.io",
        "QDRANT_API_KEY": "your-api-key",
        "COLLECTION_NAME": "bmad-knowledge"
      }
    }
  }
}
```

## Collection Configuration

### Collection Names

Choose descriptive names for your collections:

```bash
# Project-specific naming
QDRANT_KNOWLEDGE_COLLECTION=myapp-knowledge
QDRANT_BEST_PRACTICES_COLLECTION=myapp-best-practices

# Team-based naming
QDRANT_KNOWLEDGE_COLLECTION=team-alpha-knowledge
QDRANT_BEST_PRACTICES_COLLECTION=team-alpha-best-practices
```

### Vector Settings

The collections use these default settings:
- **Vector Size**: 384 (configurable via `EMBEDDING_DIMENSION`)
- **Distance Metric**: Cosine similarity
- **Index**: HNSW with default parameters

## Validation Settings

### Content Length

```bash
# Minimum content length (rejects very short entries)
MIN_CONTENT_LENGTH=100

# Maximum content length (truncates very long entries)
MAX_CONTENT_LENGTH=50000
```

### Duplicate Detection

```bash
# Similarity threshold for considering entries as duplicates
# Higher = stricter matching (fewer false positives)
# Lower = more matches (fewer false negatives)
SIMILARITY_THRESHOLD=0.85
```

## Advanced Configuration

### Using config.py Directly

All scripts import from `config.py`. You can access configuration programmatically:

```python
from config import (
    QDRANT_URL,
    KNOWLEDGE_COLLECTION,
    EMBEDDING_DIMENSION,
    validate_config,
)

# Check configuration validity
result = validate_config()
if not result['valid']:
    print(f"Config issues: {result['issues']}")
```

### Custom Configuration Module

Create a custom configuration by extending `config.py`:

```python
# my_config.py
from config import *

# Override defaults
KNOWLEDGE_COLLECTION = "custom-knowledge"
MIN_CONTENT_LENGTH = 200
```

## Troubleshooting Configuration

### Check Current Configuration

```bash
python -c "from config import validate_config; print(validate_config())"
```

### Common Issues

**"QDRANT_URL is not set"**
- Ensure `.env` file exists
- Check environment variable is exported

**"Collection not found"**
- Run `python scripts/create_collections.py`
- Verify collection name matches configuration

**"Invalid EMBEDDING_DIMENSION"**
- Must match your embedding model
- Common values: 384, 768, 1536

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.
