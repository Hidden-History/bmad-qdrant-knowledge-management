# Qdrant MCP Setup Guide

> Complete guide for using Qdrant MCP as AI assistant memory

## TL;DR

Use Qdrant MCP as an "AI assistant's memory" to prevent mistakes, track project knowledge, and maintain continuity across sessions. This guide covers what to store, deduplication, and best practices.

## Executive Summary

**Goal**: Use Qdrant MCP as an "AI assistant's memory" to prevent mistakes, track project knowledge, and maintain continuity across sessions.

**Approach**: Semi-automatic, curated knowledge base focused on high-value information that prevents costly errors.

**Benefits**:
- Prevents AI from repeating solved problems
- Maintains context across long projects
- Reduces duplicate work
- Provides instant access to critical decisions
- Self-documenting system that grows with your project

---

## Part 1: What to Store

### Tier 1: CRITICAL - Always Store

#### 1. Architecture Decisions & Constraints

**What**: Major design choices that affect multiple components
**Why**: Prevents AI from suggesting changes that violate core decisions

**Examples**:
- Database architecture decisions
- Infrastructure setup patterns
- Technology stack choices
- Integration patterns

**Storage Pattern**:
```python
mcp__qdrant__qdrant-store(
    information="Architecture decision: [Decision description with justification, trade-offs, and impacts]",
    metadata={
        "type": "architecture_decision",
        "component": "infrastructure",
        "affects": ["storage", "routing", "retrieval"],
        "decision_date": "2025-01-01",
        "breaking_change": true,
        "related_stories": ["1-3", "2-17"]
    }
)
```

#### 2. Agent Specifications & Integration Patterns

**What**: What each agent does, how to use it, common pitfalls
**Why**: Prevents misuse of agents and clarifies integration points

**Storage Pattern**:
```python
mcp__qdrant__qdrant-store(
    information="Agent [ID] ([name]): [Purpose]. Input: [description]. Output: [description]. Dependencies: [list]. CRITICAL: [Important notes].",
    metadata={
        "type": "agent_spec",
        "agent_id": "agent_15",
        "agent_name": "storage_router",
        "dependencies": ["agent_03"],
        "integration_points": ["qdrant", "postgres"],
        "common_errors": ["calling before classification complete"]
    }
)
```

#### 3. Critical Database Schemas & Constraints

**What**: Table structures, relationships, constraints that must be maintained
**Why**: Prevents schema violations and data corruption

#### 4. Common Error Patterns & Solutions

**What**: Mistakes that have been made and how to fix them
**Why**: Prevents repeating solved problems

#### 5. Story Outcomes & Implementation Notes

**What**: What was actually implemented in each story, not just what was planned
**Why**: Tracks evolution of the system, prevents assuming features exist that don't

### Tier 2: HIGH VALUE - Store When Relevant

#### 6. Configuration Patterns & Environment Setup

**What**: How to configure components correctly

#### 7. Integration Examples & Code Patterns

**What**: Working code examples for common tasks

#### 8. Performance Optimizations & Benchmarks

**What**: What works well, what doesn't

---

## Part 2: What NOT to Store

### Never Store in Qdrant MCP

| Category | Examples | Where to Store Instead |
|----------|----------|------------------------|
| **Credentials** | Passwords, API keys, tokens | .env files, secrets manager |
| **Operational Data** | Processing status, job queues, metrics | PostgreSQL tables |
| **Binary Files** | PDFs, images, documents | Filesystem, object storage |
| **Transactional Data** | User sessions, temporary state | Redis, PostgreSQL |
| **Trivial Details** | Debug logs, temporary notes, TODO comments | Code comments, task tracker |
| **Frequently Changing** | Feature flags, dynamic config | Config files, environment variables |

---

## Part 3: Preventing Duplicates

### Strategy 1: Content Hashing (Recommended)

**Pattern**: Hash content before storing, check if hash exists

```python
import hashlib

def store_knowledge_deduped(information, metadata):
    """Store only if not duplicate"""
    # Generate content hash
    content_hash = hashlib.sha256(information.encode()).hexdigest()
    metadata["content_hash"] = content_hash

    # Search for existing with same hash
    existing = mcp__qdrant__qdrant-find(
        query=f"content_hash:{content_hash}"
    )

    if existing:
        print(f"Duplicate detected: {content_hash[:8]}...")
        return "duplicate_skipped"

    # Store if unique
    mcp__qdrant__qdrant-store(
        information=information,
        metadata=metadata
    )
    return "stored"
```

### Strategy 2: Semantic Similarity Check

**Pattern**: Search before storing, check similarity threshold

```python
def store_if_novel(information, metadata, similarity_threshold=0.85):
    """Only store if semantically different from existing"""
    similar = mcp__qdrant__qdrant-find(query=information)

    if similar and similar[0]["score"] > similarity_threshold:
        print(f"Similar content exists, skipping")
        return "similar_exists"

    mcp__qdrant__qdrant-store(
        information=information,
        metadata=metadata
    )
    return "stored"
```

### Strategy 3: Unique Identifiers

**Pattern**: Include unique ID in metadata, enforce uniqueness

```python
def store_with_unique_id(information, metadata, unique_key):
    """Use unique identifier to prevent duplicates"""
    metadata["unique_id"] = unique_key  # e.g., "story-2-17", "agent-15-spec"

    existing = mcp__qdrant__qdrant-find(
        query=f"unique_id:{unique_key}"
    )

    if existing:
        return update_existing(unique_key, information, metadata)

    mcp__qdrant__qdrant-store(
        information=information,
        metadata=metadata
    )
    return "stored"
```

**Recommended**: Combine Strategy 1 + Strategy 3
- Use content hashing for exact duplicate detection
- Use unique IDs (story-id, agent-id, decision-id) for logical deduplication

---

## Part 4: Updating Changed Information

### Update Strategy 1: Versioned Entries (Recommended)

**When to Use**: Important decisions that may evolve
**Pattern**: Keep old versions marked as deprecated

### Update Strategy 2: In-Place Updates

**When to Use**: Minor corrections, clarifications
**Pattern**: Update existing entry directly

### Update Strategy 3: Append-Only Pattern

**When to Use**: Tracking changes over time
**Pattern**: Add new entries, link to previous

---

## Part 5: Metadata Structure

### Standard Metadata Schema

```python
STANDARD_METADATA = {
    # Identity
    "unique_id": "string",           # e.g., "story-2-17", "agent-15-spec"
    "content_hash": "string",        # SHA256 for deduplication
    "type": "string",                # architecture_decision, agent_spec, etc.

    # Classification
    "component": "string",           # Component affected
    "sub_component": "string",       # Specific sub-component
    "affects": ["string"],           # Which parts of system this impacts

    # Project Tracking
    "epic_id": "string",             # Epic identifier
    "story_id": "string",            # Story identifier
    "task_id": "string",             # Task identifier

    # Temporal
    "created_at": "timestamp",       # When documented
    "last_updated": "timestamp",     # Most recent update
    "deprecated": "boolean",         # Is this outdated?
    "superseded_by": "string",       # If deprecated, what replaces it?

    # Version Management
    "version": "integer",            # Version number
    "replaces": "string",            # Previous version unique_id
    "breaking_change": "boolean",    # Does this break existing patterns?

    # Quality & Context
    "importance": "string",          # critical, high, medium, low
    "confidence": "float",           # 0.0-1.0 how sure are you?
    "source": "string",              # documentation, code_review, testing, etc.

    # Search Optimization
    "keywords": ["string"],          # Key terms for search
    "related_ids": ["string"],       # Cross-references
    "search_intent": ["string"]      # How this might be searched
}
```

---

## Part 6: Recommended Workflow

### Daily Workflow

**Morning (Project Start)**:
```python
# Check recent knowledge additions
recent = mcp__qdrant__qdrant-find(
    query="recent changes last 7 days"
)

# Get context for today's work
todays_context = mcp__qdrant__qdrant-find(
    query="[today's story] implementation patterns"
)
```

**During Work**:
- AI makes note of important discoveries
- You review and approve what to store
- AI stores approved items with proper metadata

**End of Session (Critical Checkpoint)**:
```python
# Store today's outcomes
mcp__qdrant__qdrant-store(
    information="Session summary for Story [ID]...",
    metadata={...}
)
```

### Story Completion Checklist

When you complete a story, store:

1. **Implementation Summary** (what was actually built)
2. **Integration Points** (how it connects to other components)
3. **Common Errors** (pitfalls discovered during development)
4. **Testing Patterns** (how to test this feature)
5. **Configuration** (environment variables, settings needed)

---

## Part 7: Search Patterns

### Pattern 1: Find Similar Past Work

```python
similar_work = mcp__qdrant__qdrant-find(
    query="How to implement agent integration with database logging?"
)
```

### Pattern 2: Check for Known Issues

```python
solutions = mcp__qdrant__qdrant-find(
    query="Docker container connection refused postgres"
)
```

### Pattern 3: Understand Agent Usage

```python
agent_info = mcp__qdrant__qdrant-find(
    query="Agent 15 storage router how to use dependencies"
)
```

### Pattern 4: Architecture Validation

```python
constraints = mcp__qdrant__qdrant-find(
    query="qdrant tier architecture constraints"
)
```

---

## Part 8: Quick Reference Templates

### Template 1: Architecture Decision

```python
mcp__qdrant__qdrant-store(
    information="[Decision title and justification. Include trade-offs, alternatives considered, and why this was chosen.]",
    metadata={
        "unique_id": "arch-decision-[topic]-[date]",
        "type": "architecture_decision",
        "component": "[affected component]",
        "breaking_change": True/False,
        "importance": "critical",
        "affects": ["[list of impacted systems]"]
    }
)
```

### Template 2: Agent Specification

```python
mcp__qdrant__qdrant-store(
    information="""
Agent [ID] ([name]): [Purpose]

INPUT: [What it receives]
OUTPUT: [What it produces]
DEPENDENCIES: [Required agents/services]
INTEGRATION: [How to call it]
COMMON ERRORS: [Known issues]
TESTING: [Test file locations]
    """,
    metadata={
        "unique_id": "agent-[id]-spec",
        "type": "agent_spec",
        "agent_id": "[id]",
        "dependencies": ["[agent-ids]"],
        "importance": "high"
    }
)
```

### Template 3: Error Pattern

```python
mcp__qdrant__qdrant-store(
    information="""
ERROR: [Error message or symptom]
CAUSE: [Root cause explanation]
SOLUTION: [How to fix]
PREVENTION: [How to avoid in future]
    """,
    metadata={
        "unique_id": "error-[short-description]",
        "type": "error_pattern",
        "component": "[affected system]",
        "severity": "[critical/high/medium/low]"
    }
)
```

---

## Part 9: Success Metrics

### How You'll Know It's Working

1. **Reduced Repeated Mistakes**
   - AI checks knowledge base before implementing
   - Finds past solutions instead of reinventing

2. **Faster Onboarding**
   - New AI agents/team members can search for context
   - Self-documenting system

3. **Better Decision Making**
   - Can quickly find why decisions were made
   - Avoid contradicting past choices

4. **Improved Continuity**
   - Resume work after breaks without re-learning
   - Context preserved across sessions

### Monthly Review Checklist

- [ ] Are searches finding relevant results?
- [ ] Is duplicate knowledge being stored?
- [ ] Are deprecated entries marked correctly?
- [ ] Have new agents/features been documented?
- [ ] Are error patterns being captured?

---

## Final Recommendation

**Start Simple, Grow Organically**:

1. **This Week**: Store top 10 critical items (architecture, agents, schemas)
2. **Ongoing**: Add 3-5 entries per story completion
3. **Monthly**: Review and clean up duplicates/outdated

**Quality Over Quantity**:
- 50 high-quality, well-organized entries > 500 random notes
- Each entry should answer: "What will AI need to know to avoid mistakes?"

**Success Pattern**:
```
Before implementing → Search knowledge base
During work → Note important discoveries
After completion → Store validated learnings
Weekly review → Deprecate outdated, add cross-refs
```

This approach transforms Qdrant MCP from a "dump everything" database into a curated "institutional memory" that makes your AI assistant smarter with every story you complete.
