# Metadata Schemas

> JSON Schema definitions for all knowledge types

## Overview

These schemas define the required and optional metadata fields for each knowledge type. All entries are validated against these schemas before storage.

## Schema Files

| Schema | Knowledge Type | Purpose |
|--------|----------------|---------|
| `architecture_decision.json` | `architecture_decision` | Major design choices and constraints |
| `agent_spec.json` | `agent_spec` | Agent capabilities and integration patterns |
| `story_outcome.json` | `story_outcome` | Completed story implementations |
| `error_pattern.json` | `error_pattern` | Common errors and solutions |
| `database_schema.json` | `database_schema` | Table structures and constraints |
| `config_pattern.json` | `config_pattern` | Configuration examples |
| `integration_example.json` | `integration_example` | Working integration code |
| `best_practice.json` | `best_practice` | Universal patterns (agent-discovered) |

## Common Required Fields

All schemas require these base fields:

| Field | Type | Description |
|-------|------|-------------|
| `unique_id` | string | Unique identifier (pattern: `{type}-{topic}-{date}`) |
| `type` | string | Knowledge type (must match schema) |
| `component` | string | Primary system component |
| `importance` | enum | `critical`, `high`, `medium`, `low` |
| `created_at` | date | Creation date (YYYY-MM-DD) |

## Schema Details

### architecture_decision.json

**Required Fields:**
- `unique_id` - Pattern: `arch-decision-{topic}-{YYYY-MM-DD}`
- `type` - Must be `"architecture_decision"`
- `component` - System component (qdrant, postgres, api, etc.)
- `importance` - Impact level
- `created_at` - Date
- `breaking_change` - Boolean

**Optional Fields:**
- `affects` - Array of impacted systems
- `alternatives_considered` - Other options evaluated
- `trade_offs` - Pros and cons object
- `migration_required` - Boolean
- `deprecated` - Boolean (default: false)
- `superseded_by` - ID of replacement decision

### agent_spec.json

**Required Fields:**
- `unique_id` - Pattern: `agent-spec-{agent}-{YYYY-MM-DD}`
- `type` - Must be `"agent_spec"`
- `agent_id` - Agent identifier
- `component` - Primary component
- `importance` - Impact level
- `created_at` - Date

**Optional Fields:**
- `capabilities` - Array of what agent can do
- `dependencies` - Required services/agents
- `integration_points` - How to integrate
- `common_errors` - Known issues

### story_outcome.json

**Required Fields:**
- `unique_id` - Pattern: `story-{epic}-{story}-{YYYY-MM-DD}`
- `type` - Must be `"story_outcome"`
- `story_id` - Story identifier (e.g., "1-3")
- `epic_id` - Epic identifier
- `component` - Primary component
- `importance` - Impact level
- `created_at` - Date

**Optional Fields:**
- `files_modified` - Array of changed files
- `tests_added` - Array of test files
- `integration_points` - Connection points

### error_pattern.json

**Required Fields:**
- `unique_id` - Pattern: `error-{component}-{type}-{YYYY-MM-DD}`
- `type` - Must be `"error_pattern"`
- `component` - Where error occurs
- `error_type` - Category of error
- `importance` - Severity
- `created_at` - Date

**Optional Fields:**
- `symptoms` - Array of indicators
- `root_cause` - Why it happens
- `solution` - How to fix
- `prevention` - How to avoid

## Customization

### Adding New Components

Edit the `component` enum in each schema:

```json
"component": {
  "type": "string",
  "enum": [
    "qdrant",
    "postgres",
    "your-new-component"  // Add here
  ]
}
```

### Adding New Fields

Add to the `properties` object:

```json
"properties": {
  "your_new_field": {
    "type": "string",
    "description": "What this field captures"
  }
}
```

To make it required, add to the `required` array.

### Creating New Knowledge Types

1. Copy the closest existing schema
2. Update `title`, `description`, and `type` const
3. Modify required and optional fields
4. Add to `validation/validate_metadata.py` ALLOWED_TYPES
5. Create example in `example_population/`

## Validation

### Using the Validation Script

```bash
# Validate metadata against schema
python validation/validate_metadata.py --metadata entry.json --type architecture_decision

# Auto-detect type from metadata
python validation/validate_metadata.py --metadata entry.json --auto-detect
```

### Programmatic Validation

```python
from jsonschema import validate
import json

with open("metadata-schemas/architecture_decision.json") as f:
    schema = json.load(f)

metadata = {
    "unique_id": "arch-decision-auth-2025-01-01",
    "type": "architecture_decision",
    "component": "api",
    "importance": "high",
    "created_at": "2025-01-01",
    "breaking_change": False
}

validate(instance=metadata, schema=schema)  # Raises on error
```

## Related Documentation

- [validation/](../validation/) - Validation scripts and tests
- [CONFIGURATION.md](../CONFIGURATION.md) - Configuration options
- [BMAD_INTEGRATION_RULES.md](../BMAD_INTEGRATION_RULES.md) - Agent enforcement rules
