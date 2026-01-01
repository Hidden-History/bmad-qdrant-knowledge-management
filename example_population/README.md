# Example Population Scripts

> Sample scripts demonstrating how to populate your knowledge base

## Overview

These example scripts show the proper format and validation for storing different types of knowledge in your Qdrant collections.

## Scripts

| Script | Knowledge Type | Description |
|--------|---------------|-------------|
| `example_architecture_decision.py` | `architecture_decision` | Major design choices and constraints |
| `example_agent_spec.py` | `agent_spec` | Agent specifications and integration patterns |
| `example_story_outcome.py` | `story_outcome` | Completed story implementations |

## Usage

### Running Examples

```bash
# Run any example to see the structure and validation
python example_population/example_architecture_decision.py
python example_population/example_agent_spec.py
python example_population/example_story_outcome.py
```

### Creating Your Own

1. Copy the example closest to your knowledge type
2. Modify the `INFORMATION` content
3. Update the `METADATA` dictionary
4. Run to validate before storing

## Content Guidelines

### Architecture Decisions

Include:
- **DECISION**: What was decided
- **JUSTIFICATION**: Why this choice
- **TRADE-OFFS**: Pros and cons
- **IMPACTS**: What systems are affected
- **ALTERNATIVES**: Other options considered

### Agent Specifications

Include:
- **PURPOSE**: What the agent does
- **INPUT**: Expected inputs
- **OUTPUT**: What it produces
- **DEPENDENCIES**: Required services/agents
- **INTEGRATION**: How to use it
- **COMMON ERRORS**: Known issues and solutions

### Story Outcomes

Include:
- **WHAT WAS BUILT**: Deliverables
- **INTEGRATION POINTS**: How it connects
- **COMMON ERRORS**: Issues discovered
- **TESTING**: Test coverage and files
- **FILES MODIFIED**: Changed files

## Validation

All scripts validate:
- Required metadata fields
- Valid knowledge types
- Importance levels
- Content hash for deduplication

## Storing to Qdrant

The example scripts show the structure but don't actually store to Qdrant. To store:

### Option 1: Use MCP in Claude

```python
mcp__qdrant__qdrant-store(
    information="Your content here",
    metadata={
        "unique_id": "your-unique-id",
        "type": "architecture_decision",
        "component": "your-component",
        "importance": "critical",
        "created_at": "2025-01-01"
    }
)
```

### Option 2: Use Qdrant Python Client

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Connect
client = QdrantClient(url="http://localhost:6333")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Generate embedding
embedding = model.encode(INFORMATION).tolist()

# Store
client.upsert(
    collection_name="bmad-knowledge",
    points=[{
        "id": str(uuid.uuid4()),
        "vector": embedding,
        "payload": {"information": INFORMATION, **METADATA}
    }]
)
```

### Option 3: Use Bulk Population Script

```bash
# Modify scripts/populate_knowledge_base_optimized.py
# to point to your population scripts, then run:
python scripts/populate_knowledge_base_optimized.py
```

## Related Documentation

- [BMAD_INTEGRATION_RULES.md](../BMAD_INTEGRATION_RULES.md) - Complete storage rules
- [QDRANT_MCP_SETUP_GUIDE.md](../QDRANT_MCP_SETUP_GUIDE.md) - What to store and why
- [metadata-schemas/](../metadata-schemas/) - JSON schemas for validation
