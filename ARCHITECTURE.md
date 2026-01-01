# Architecture Guide

> System design and component overview

## TL;DR

Two Qdrant collections store knowledge as vectors. Scripts validate and deduplicate before storage. Claude MCP provides the interface for AI agents to search and store.

## System Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                    Knowledge Management System                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                     INPUT LAYER                               │ │
│  │                                                                │ │
│  │   BMAD Workflows        Manual Storage      Population        │ │
│  │   (dev-story, etc.)     (Claude MCP)        Scripts           │ │
│  └────────────────────────────┬─────────────────────────────────┘ │
│                               │                                    │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                   VALIDATION LAYER                            │ │
│  │                                                                │ │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │ │
│  │   │ Schema      │  │ Duplicate   │  │ Content             │  │ │
│  │   │ Validation  │  │ Detection   │  │ Validation          │  │ │
│  │   └─────────────┘  └─────────────┘  └─────────────────────┘  │ │
│  └────────────────────────────┬─────────────────────────────────┘ │
│                               │                                    │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    STORAGE LAYER                              │ │
│  │                                                                │ │
│  │   ┌─────────────────────────┐  ┌─────────────────────────┐   │ │
│  │   │   Knowledge Collection  │  │ Best Practices Collection│   │ │
│  │   │   (7 types)             │  │ (1 type)                │   │ │
│  │   │                         │  │                          │   │ │
│  │   │ - architecture_decision │  │ - best_practice          │   │ │
│  │   │ - agent_spec            │  │                          │   │ │
│  │   │ - story_outcome         │  │                          │   │ │
│  │   │ - error_pattern         │  │                          │   │ │
│  │   │ - database_schema       │  │                          │   │ │
│  │   │ - config_pattern        │  │                          │   │ │
│  │   │ - integration_example   │  │                          │   │ │
│  │   └─────────────────────────┘  └─────────────────────────┘   │ │
│  └────────────────────────────┬─────────────────────────────────┘ │
│                               │                                    │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                   RETRIEVAL LAYER                             │ │
│  │                                                                │ │
│  │   Semantic Search → Vector Similarity → Metadata Filtering    │ │
│  └────────────────────────────┬─────────────────────────────────┘ │
│                               │                                    │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                     OUTPUT                                    │ │
│  │                                                                │ │
│  │   AI Agents receive relevant past knowledge for current work  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Input Layer

Entry points for knowledge:

- **BMAD Workflows** - Automatic storage triggered by story completion, architecture decisions
- **Manual Storage** - Direct storage via Claude MCP `qdrant-store`
- **Population Scripts** - Bulk loading for initial setup or migration

### 2. Validation Layer

Three-stage validation before storage:

#### Schema Validation (`validate_metadata.py`)
- JSON Schema Draft 7 validation
- Required fields: `unique_id`, `type`, `component`, `importance`, `created_at`
- Type-specific field validation
- Format checking (dates, IDs)

#### Duplicate Detection (`check_duplicates.py`)
- **Content Hash** - SHA256 hash of content prevents exact duplicates
- **Semantic Similarity** - Vector similarity check (threshold: 0.85)
- **Unique ID Collision** - Prevents ID conflicts

#### Content Validation
- Minimum length: 100 characters
- Maximum length: 50,000 characters
- Forbidden patterns check (credentials, secrets)

### 3. Storage Layer

Two Qdrant collections with different purposes:

#### Knowledge Collection
**Purpose:** Project-specific institutional memory

**Types (7):**
| Type | Description |
|------|-------------|
| `architecture_decision` | Major design choices and constraints |
| `agent_spec` | Agent capabilities and integration patterns |
| `story_outcome` | Completed story implementations |
| `error_pattern` | Common errors and solutions |
| `database_schema` | Table structures and constraints |
| `config_pattern` | Configuration examples |
| `integration_example` | Working integration code |

#### Best Practices Collection
**Purpose:** Universal patterns that apply across projects

**Types (1):**
| Type | Description |
|------|-------------|
| `best_practice` | Performance, security, scalability patterns |

### 4. Retrieval Layer

How knowledge is found:

1. **Semantic Search** - Natural language query converted to vector
2. **Vector Similarity** - Find entries with similar meaning
3. **Metadata Filtering** - Optional filtering by type, component, importance
4. **Ranking** - Results ordered by relevance

### 5. Output

AI agents receive:
- Relevant past work before implementing
- Known error patterns to avoid
- Architecture constraints to follow
- Integration patterns to reuse

## Data Flow

### Storage Flow

```
Content + Metadata
       │
       ▼
┌─────────────────┐
│ Generate Hash   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Duplicate │─── Exists? ──→ Update/Skip
└────────┬────────┘
         │ New
         ▼
┌─────────────────┐
│ Validate Schema │─── Invalid? ─→ Error
└────────┬────────┘
         │ Valid
         ▼
┌─────────────────┐
│ Route to        │
│ Collection      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Vector │
│ (Embedding)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Store in Qdrant │
└─────────────────┘
```

### Search Flow

```
Natural Language Query
         │
         ▼
┌─────────────────┐
│ Generate Query  │
│ Vector          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Search Qdrant   │
│ Collections     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Rank by         │
│ Similarity      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Return Top      │
│ Results         │
└─────────────────┘
```

## Metadata Schema

All entries share a common metadata structure:

```json
{
  "unique_id": "arch-decision-database-20250101",
  "type": "architecture_decision",
  "component": "database",
  "importance": "critical",
  "created_at": "2025-01-01",
  "content_hash": "sha256:abc123...",

  // Type-specific fields
  "breaking_change": true,
  "affects": ["api", "frontend"],
  "rationale": "..."
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `unique_id` | string | Unique identifier, format: `{type}-{topic}-{date}` |
| `type` | enum | One of 8 knowledge types |
| `component` | string | System component affected |
| `importance` | enum | critical, high, medium, low |
| `created_at` | date | ISO 8601 date |

### Type-Specific Fields

See `metadata-schemas/` directory for complete schemas per type.

## Vector Configuration

### Embedding Model

Default: `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Good balance of quality and speed
- Runs locally, no API needed

### Collection Settings

- **Distance Metric:** Cosine similarity
- **Index:** HNSW (Hierarchical Navigable Small World)
- **Quantization:** None (full precision)

## Integration Points

### BMAD Workflows

Integration with BMAD-METHOD:

1. **dev-story** - Can trigger knowledge storage on completion
2. **sprint-planning** - Search for related past work
3. **party-mode** - All agents access shared knowledge
4. **code-review** - Check for known patterns

### Claude MCP

Two MCP tools available:

1. **qdrant-find** - Semantic search
   ```python
   results = mcp__qdrant__qdrant-find(query="search terms")
   ```

2. **qdrant-store** - Store new knowledge
   ```python
   mcp__qdrant__qdrant-store(
       information="content",
       metadata={...}
   )
   ```

## Security Considerations

### What's Protected

- No credentials stored in code
- API keys loaded from environment
- Content validated before storage
- Forbidden patterns checked

### What's NOT Stored

- Passwords, API keys, tokens
- Private keys, certificates
- Personal information
- Transactional data

## Scaling Considerations

### Local Development
- Single Qdrant instance sufficient
- All collections on same server
- Docker with persistent volume

### Production
- Consider Qdrant Cloud for reliability
- Separate collections for large projects
- Regular backups recommended

## Design Decisions

### Why Two Collections?

1. **Separation of Concerns** - Project knowledge vs universal patterns
2. **Different Lifecycles** - Best practices rarely change, project knowledge evolves
3. **Sharing** - Best practices can be shared across projects

### Why Qdrant?

1. **Vector Search** - Semantic similarity for natural language queries
2. **MCP Support** - Official MCP server available
3. **Easy Setup** - Docker image, cloud option
4. **Metadata** - Rich payload storage with filtering

### Why Validation Before Storage?

1. **Data Quality** - Consistent metadata structure
2. **Deduplication** - No redundant entries
3. **Security** - No sensitive data stored
4. **Maintainability** - Easier cleanup and review
