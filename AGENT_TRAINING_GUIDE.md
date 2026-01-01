# Agent Training Guide: Qdrant MCP Knowledge Management

> Training guide for BMAD agents using Qdrant MCP institutional memory

## TL;DR

1. **SEARCH FIRST** - Always check existing knowledge before implementing
2. **STORE MANDATORY** - Store all story outcomes, architecture changes, critical errors
3. **VALIDATE ALWAYS** - Use validation scripts before storing

---

## Quick Start for Agents

### Your First 5 Minutes

```python
# Step 1: Search for similar work
results = mcp__qdrant__qdrant-find(
    query="agent integration database logging"
)

# Step 2: If found, read and apply learnings
# Step 3: If not found, implement and store outcome
# Step 4: After story completion, store the outcome
```

---

## Core Concepts

### What is Qdrant MCP?

Qdrant MCP is the project's **institutional memory system** that:
- Prevents AI from repeating mistakes
- Maintains continuity across sessions
- Provides instant access to past solutions
- Documents critical architectural decisions
- Stores error patterns and solutions

### When to Use It

| Scenario | Action | Why |
|----------|--------|-----|
| **Starting new story** | Search knowledge base | Find similar past work |
| **Discovering error** | Search for error pattern | Solution might exist |
| **Story completion** | Store outcome | Document for future |
| **Architecture change** | Store decision | Critical for continuity |
| **Agent creation/update** | Store spec | Integration reference |

---

## Searching Knowledge

### Search Strategy

**1. Use Short, Focused Queries (2-5 keywords)**

GOOD Queries:
```python
mcp__qdrant__qdrant-find(query="agent routing logic")
mcp__qdrant__qdrant-find(query="qdrant tier ports")
mcp__qdrant__qdrant-find(query="docker postgres connection")
```

BAD Queries (too long, unfocused):
```python
mcp__qdrant__qdrant-find(query="how to implement the agent storage routing logic with tier assignment and port mapping validation")
```

**2. Search Multiple Perspectives**

```python
# Technical search
mcp__qdrant__qdrant-find(query="qdrant tier architecture")

# Component search
mcp__qdrant__qdrant-find(query="agent dependencies")

# Error search
mcp__qdrant__qdrant-find(query="connection refused postgres")
```

### Common Search Patterns

| Need | Query Example |
|------|---------------|
| Agent usage | `"Agent 15 integration"` |
| Database schema | `"chunks table schema"` |
| Error solution | `"Docker postgres refused"` |
| Architecture | `"tier architecture ports"` |
| Configuration | `"docker compose setup"` |

---

## Storing Knowledge

### Mandatory Storage Triggers

**ALWAYS store when:**

| Event | Knowledge Type | unique_id Format |
|-------|----------------|------------------|
| Story completion | `story_outcome` | `story-{epic}-{story}-complete` |
| Architecture change (breaking) | `architecture_decision` | `arch-decision-{topic}-{YYYYMMDD}` |
| Agent create/update | `agent_spec` | `agent-{id}-spec` |
| Database migration | `database_schema` | `schema-{table}-migration-{num}` |
| Critical error discovery | `error_pattern` | `error-{desc}-{YYYYMMDD}` |

### Storage Workflow

1. Validate metadata against schema
2. Check for duplicates (content hash + semantic similarity)
3. Store to appropriate collection
4. Update tracking inventory

---

## Knowledge Content Guidelines

### Story Outcomes (Required Structure)

```markdown
Story {story_id}: {story_title}

WHAT WAS BUILT:
- Primary deliverable 1
- Primary deliverable 2
- Infrastructure added

INTEGRATION POINTS:
- Component A provides X
- Component B consumes Y
- Configuration requirements

COMMON ERRORS DISCOVERED:
- Error: "Error message"
  Cause: Root cause
  Solution: Fix applied
  Prevention: How to avoid

TESTING:
- Unit tests: file_path (count)
- Integration: file_path (count)
- E2E: coverage description
```

### Error Patterns (Required Structure)

```markdown
ERROR: {Error message or symptom}

SYMPTOM: {What you observe}

CAUSE: {Root cause analysis}

SOLUTION:
1. Step 1
2. Step 2
3. Step 3

PREVENTION:
- Preventive measure 1
- Preventive measure 2
```

### Architecture Decisions (Required Structure)

```markdown
DECISION: {What was decided}

JUSTIFICATION:
- Reason 1
- Reason 2

TRADE-OFFS:
- Pro 1
- Con 1

IMPACTS:
- Impact on component A
- Impact on component B
```

---

## Validation Workflow

### Before Storing (Automatic)

The workflow validates:
1. **Metadata schema** - Matches JSON schema for knowledge type
2. **Required fields** - All required metadata present
3. **Duplicates** - No exact or near-duplicate entries (>85% similarity)

### If Validation Fails

**Schema validation error**:
```
ERROR: Metadata validation failed
  - Missing required field: 'unique_id'
  - Invalid importance: must be critical/high/medium/low
```

**Solution**: Fix metadata or let auto-generation handle it

**Duplicate detected**:
```
INFO: Similar knowledge found (92% similarity)
  Existing ID: story-2-17-complete
```

**Options**:
- Skip (if >95% similar - exact duplicate)
- Store anyway (if adding new information)
- Update existing (retrieve and modify)

---

## Common Mistakes to Avoid

### DON'T Store

| What | Why | Instead |
|------|-----|---------|
| Credentials, API keys | Security risk | Use environment variables |
| Trivial config changes | Noise | Only store significant patterns |
| Raw documents/PDFs | Wrong system | Use document processing pipeline |
| Frequently changing data | Will become stale | Use databases |
| Implementation details | Too granular | Focus on patterns and learnings |

### DON'T Search With

| Bad Query | Why Bad | Good Query |
|-----------|---------|------------|
| Full sentences | Too specific, poor matches | 2-5 keywords |
| Keyword dumps | Unfocused, conflicting terms | Related technical terms |
| Generic terms | "error", "fix" - too broad | Specific error or component |

### DON'T Skip

| Never Skip | Why Critical |
|-----------|--------------|
| Story outcome storage | Future continuity depends on it |
| Architecture decision docs | Breaking changes must be documented |
| Critical error patterns | Prevents repeating mistakes |

---

## Troubleshooting Guide

### Can't Find Stored Knowledge

**Problem**: Search returns no results but knowledge was stored

**Solutions**:
1. Try alternative keywords from metadata
2. Search by component: `"agent_15 implementation"`
3. Search by type: `"story_outcome classification"`
4. Check knowledge_inventory.md for entry
5. Verify storage succeeded (check for success message)

### Storage Fails

**Problem**: Storage attempt fails with error

**Common Causes & Solutions**:

| Error | Cause | Solution |
|-------|-------|----------|
| "Metadata validation failed" | Missing required fields | Check schema |
| "API key not set" | Environment variable missing | Set in .env |
| "Collection not found" | Qdrant not initialized | Run collection creation script |

### Duplicate Warnings

**Problem**: Getting duplicate warnings but content is different

**Possible Reasons**:
1. **High similarity (85-95%)** - Content is very similar but not identical
   - Review existing entry
   - Decide if new information justifies storage
   - Consider updating existing instead

2. **Same unique_id** - ID collision
   - Use more specific unique_id
   - Add date or version to ID

---

## Success Metrics

You're using Qdrant MCP effectively when:

- **Search before implement** - You find relevant past work 60%+ of the time
- **Reduced rework** - Not repeating mistakes from previous stories
- **Faster ramp-up** - New sessions resume context within 5 minutes
- **Consistent patterns** - Following established architectural patterns
- **Knowledge coverage** - All completed stories have stored outcomes

---

## Quick Reference Links

| Document | Purpose |
|----------|---------|
| **QDRANT_MCP_SETUP_GUIDE.md** | Complete implementation guide |
| **BMAD_INTEGRATION_RULES.md** | Strict enforcement rules |
| **tracking/knowledge_inventory.md** | Current knowledge base contents |
| **validation/validate_metadata.py** | Metadata validation script |
| **validation/check_duplicates.py** | Duplicate detection script |

---

## Pro Tips

1. **Search FIRST** - 30 seconds of searching can save 2 hours of implementation
2. **Use metadata keywords** - Search using technical terms from metadata
3. **Store incrementally** - Don't wait until story end to store critical discoveries
4. **Read similar stories** - Learn from past implementations before coding
5. **Update inventory** - Run update_inventory.py monthly for clean audit trail

---

## Getting Help

**If you get stuck**:

1. Check this guide first
2. Read QDRANT_MCP_SETUP_GUIDE.md for detailed examples
3. Search knowledge base: `mcp__qdrant__qdrant-find(query="your problem")`
4. Review BMAD_INTEGRATION_RULES.md for compliance requirements
5. Ask user if integration rules are unclear

**Remember**: The goal is institutional memory, not perfect documentation. Store enough to prevent repeating work, not everything you do.

---

## Training Complete

You now know how to:
- Search knowledge base effectively
- Store knowledge when mandatory
- Validate before storage
- Avoid common mistakes
- Troubleshoot issues

**Next**: Apply this knowledge to your next story! Search first, implement, then store outcomes.
