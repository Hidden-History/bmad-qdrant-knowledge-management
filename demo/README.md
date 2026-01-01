# Demo Knowledge Entries

This folder contains example knowledge entries showing what a populated knowledge base looks like.

## Files

| File | Knowledge Type | Description |
|------|----------------|-------------|
| `architecture_decision.json` | `architecture_decision` | Example architecture decision record |
| `agent_spec.json` | `agent_spec` | Example agent specification |
| `story_outcome.json` | `story_outcome` | Example completed story |
| `error_pattern.json` | `error_pattern` | Example error and solution |

## Usage

These examples demonstrate:
- Proper metadata structure
- ID naming conventions (`{type}-{component}-{date}`)
- Cross-referencing between entries
- Content formatting best practices

## Loading Demo Data

```python
import json
from pathlib import Path

demo_dir = Path("demo")
for json_file in demo_dir.glob("*.json"):
    with open(json_file) as f:
        entry = json.load(f)
        print(f"Loading: {entry['metadata']['unique_id']}")
        # Use mcp__qdrant__qdrant-store to add to your collection
```

## Note

These are examples only. Modify the `group_id` to match your project before storing.
