# Qdrant Collection Setup Guide

> Two-collection architecture for knowledge management

## TL;DR

Single Qdrant server with two collections: one for project-specific knowledge, one for universal best practices. Collections are configurable via environment variables.

---

## Collection Architecture

### Collection 1: Knowledge Collection

**Default Name**: `bmad-knowledge` (configurable via `QDRANT_KNOWLEDGE_COLLECTION`)
**Purpose**: Project-specific institutional memory

**Stores**:
1. **Architecture Decisions** (`architecture_decision`)
   - Major design choices affecting multiple components
   - Breaking changes and technical constraints
   - Infrastructure decisions

2. **Agent Specifications** (`agent_spec`)
   - Agent capabilities and integration points
   - Dependencies and calling patterns
   - Common errors and pitfalls

3. **Story Outcomes** (`story_outcome`)
   - Completed story implementations
   - Integration points and lessons learned
   - Testing patterns and file modifications

4. **Error Patterns** (`error_pattern`)
   - Recurring errors and solutions
   - Root causes and prevention strategies
   - Reproduction steps

5. **Database Schemas** (`database_schema`)
   - Table structures and constraints
   - Migration patterns
   - Relationships and indexes

6. **Configuration Patterns** (`config_pattern`)
   - Validated configuration examples
   - Environment variable requirements
   - Security considerations

7. **Integration Examples** (`integration_example`)
   - Working code examples
   - Data flow patterns
   - Error handling approaches

**Vector Dimensions**: 384 (sentence-transformers/all-MiniLM-L6-v2)
**Expected Volume**: ~500-1000 entries over project lifetime
**Update Frequency**: Per story completion (15-25 entries per sprint)

---

### Collection 2: Best Practices Collection

**Default Name**: `bmad-best-practices` (configurable via `QDRANT_BEST_PRACTICES_COLLECTION`)
**Purpose**: Agent-discovered industry best practices

**Stores**:
1. **Best Practices** (`best_practice`)
   - Performance optimizations
   - Security patterns
   - Scalability approaches
   - Architecture patterns
   - Code quality improvements
   - Configuration best practices

**Vector Dimensions**: 384 (sentence-transformers/all-MiniLM-L6-v2)
**Expected Volume**: ~200-500 entries over project lifetime
**Update Frequency**: Continuous (agents discover during research)

**Key Difference**: These are **universal** best practices applicable across projects, not specific to your implementation details.

---

## Qdrant MCP Server Configuration

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

### Dual Collection Configuration (More Flexible)

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

**Recommendation**: Use basic configuration initially. Switch to dual collection if you need more isolation.

---

## Collection Initialization

### Prerequisites

1. **Qdrant Server Running**:
   ```bash
   curl http://localhost:6333/health
   ```

2. **Qdrant MCP Server Installed**:
   ```bash
   npx -y @modelcontextprotocol/server-qdrant --help
   ```

### Creating Collections

Use the provided script:

```bash
python scripts/create_collections.py
```

Or manually with Python:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url="http://localhost:6333")

# Knowledge Collection
client.create_collection(
    collection_name="bmad-knowledge",
    vectors_config=VectorParams(
        size=384,  # sentence-transformers/all-MiniLM-L6-v2
        distance=Distance.COSINE
    )
)

# Best Practices Collection
client.create_collection(
    collection_name="bmad-best-practices",
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)
```

Or with REST API:

```bash
# Knowledge Collection
curl -X PUT http://localhost:6333/collections/bmad-knowledge \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 384, "distance": "Cosine"}}'

# Best Practices Collection
curl -X PUT http://localhost:6333/collections/bmad-best-practices \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 384, "distance": "Cosine"}}'
```

---

## Verifying Collections

### Check Collections Exist

```bash
curl http://localhost:6333/collections
```

### Get Collection Info

```bash
curl http://localhost:6333/collections/bmad-knowledge
curl http://localhost:6333/collections/bmad-best-practices
```

### Check Collection Size

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

knowledge_info = client.get_collection("bmad-knowledge")
practices_info = client.get_collection("bmad-best-practices")

print(f"bmad-knowledge: {knowledge_info.points_count} points")
print(f"bmad-best-practices: {practices_info.points_count} points")
```

---

## Usage Patterns

### Storing to Specific Collection

#### Project Knowledge (Default)
```python
mcp__qdrant__qdrant-store(
    information="Story implementation details...",
    metadata={
        "unique_id": "story-2-17-complete",
        "type": "story_outcome",
        # ... other metadata
    }
)
```

#### Best Practices
```python
mcp__qdrant__qdrant-store(
    information="Performance optimization pattern...",
    metadata={
        "unique_id": "bp-qdrant-batch-upsert-2025-01-01",
        "type": "best_practice",
        "discovered_by": "agent_15",
        # ... other metadata
    },
    collection="bmad-best-practices"  # Explicit collection
)
```

### Searching Collections

#### Search Project Knowledge
```python
results = mcp__qdrant__qdrant-find(
    query="storage routing tier assignment"
)
```

#### Search Best Practices
```python
results = mcp__qdrant__qdrant-find(
    query="qdrant performance optimization",
    collection="bmad-best-practices"
)
```

---

## Collection Comparison

| Feature | Knowledge Collection | Best Practices Collection |
|---------|---------------------|--------------------------|
| **Purpose** | Project-specific memory | Universal best practices |
| **Types** | 7 types | 1 type |
| **Source** | Project implementation | Agent research |
| **Storage** | Manual (story completion) | Automatic (agent discovery) |
| **Scope** | Your project only | Cross-project applicable |
| **Update Frequency** | Per sprint (15-25/sprint) | Continuous |
| **Expected Volume** | 500-1000 entries | 200-500 entries |

---

## Maintenance

### Regular Tasks

**Weekly**:
- Check collection sizes
- Verify no duplicate entries
- Review deprecated entries

**Monthly**:
- Review search quality
- Update outdated best practices
- Clean up superseded entries

### Backup Strategy

```bash
# Create snapshots
curl -X POST http://localhost:6333/collections/bmad-knowledge/snapshots
curl -X POST http://localhost:6333/collections/bmad-best-practices/snapshots
```

---

## Customizing Collection Names

Update your `.env` file:

```bash
QDRANT_KNOWLEDGE_COLLECTION=my-project-knowledge
QDRANT_BEST_PRACTICES_COLLECTION=my-project-best-practices
```

Then run:

```bash
python scripts/create_collections.py
```

The scripts will use your custom collection names.

---

## FAQ

**Q: Why two collections instead of one?**
A: Separation of concerns. Project knowledge is specific to your implementation. Best practices are universal patterns applicable across projects. This separation:
- Makes search more targeted
- Allows different update/review cycles
- Enables sharing best practices across projects
- Prevents project-specific details from polluting universal patterns

**Q: Can I use different embedding models for each collection?**
A: Yes, if using dual server configuration. However, using the same model (all-MiniLM-L6-v2) ensures cross-collection compatibility.

**Q: How do I know which collection to search?**
A:
- Searching for project-specific info (agent specs, story outcomes)? → Knowledge collection
- Searching for optimization patterns, best practices? → Best practices collection
- Not sure? Search both and combine results

**Q: Can agents automatically choose the correct collection?**
A: Yes, based on metadata type:
- Types: `architecture_decision`, `agent_spec`, `story_outcome`, `error_pattern`, `database_schema`, `config_pattern`, `integration_example` → Knowledge collection
- Type: `best_practice` → Best practices collection

---

## Related Documentation

- [CONFIGURATION.md](./CONFIGURATION.md) - Environment configuration
- [BMAD_INTEGRATION_RULES.md](./BMAD_INTEGRATION_RULES.md) - Agent enforcement rules
- [QUICKSTART.md](./QUICKSTART.md) - Quick setup guide
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
