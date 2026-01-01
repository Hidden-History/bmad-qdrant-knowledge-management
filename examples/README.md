# Usage Examples

> Code examples demonstrating how to search and store knowledge

## Overview

These examples show practical usage patterns for interacting with your Qdrant knowledge base.

## Files

| File | Purpose | Description |
|------|---------|-------------|
| `search_patterns.py` | Querying | Common search patterns for finding knowledge |
| `store_architecture_decision.py` | Storing | How to store architecture decisions |
| `store_agent_spec.py` | Storing | How to store agent specifications |
| `store_best_practice.py` | Storing | How to store best practices |

## Search Patterns

The `search_patterns.py` script demonstrates effective queries:

```bash
python examples/search_patterns.py
```

### Common Search Use Cases

| Use Case | Example Query |
|----------|---------------|
| Find past solutions | `"authentication error handling"` |
| Check architecture | `"database connection pooling decision"` |
| Find agent usage | `"how to use validation agent"` |
| Error solutions | `"timeout error postgres"` |

### Using MCP Search

```python
# In Claude with MCP configured
results = mcp__qdrant__qdrant-find(query="authentication patterns")
```

## Store Examples

Each store example shows the complete workflow:

1. Define the content (INFORMATION)
2. Create metadata dictionary
3. Validate against schema
4. Store to Qdrant

### Running Store Examples

```bash
# Preview what would be stored (validation only)
python examples/store_architecture_decision.py

# Actually store (uncomment the store call in the script)
python examples/store_architecture_decision.py
```

## Customization

When adapting these examples for your project:

| What to Change | Location | Example |
|----------------|----------|---------|
| Collection name | `.env` file | `QDRANT_KNOWLEDGE_COLLECTION=my-project-knowledge` |
| Group ID | Metadata dict | `"group_id": "my-project"` |
| Component values | Metadata dict | Match your system components |
| Unique ID format | Metadata dict | Follow `{type}-{topic}-{date}` pattern |

## Integration with MCP

### Store via MCP (Recommended)

```python
mcp__qdrant__qdrant-store(
    information="Your knowledge content here...",
    metadata={
        "unique_id": "arch-decision-auth-flow-2025-01-01",
        "type": "architecture_decision",
        "component": "api",
        "importance": "high",
        "created_at": "2025-01-01",
        "breaking_change": false
    }
)
```

### Search via MCP

```python
# Semantic search
results = mcp__qdrant__qdrant-find(query="how does authentication work")

# The results include:
# - information: The stored content
# - metadata: All metadata fields
# - score: Relevance score
```

## Related Documentation

- [example_population/](../example_population/) - Template scripts for bulk population
- [metadata-schemas/](../metadata-schemas/) - JSON schemas defining valid metadata
- [BMAD_INTEGRATION_RULES.md](../BMAD_INTEGRATION_RULES.md) - Storage rules for BMAD agents
