# Knowledge Tracking

> Templates for tracking and reviewing your knowledge base

## Overview

This folder contains templates for maintaining visibility into your knowledge base contents and scheduling regular reviews.

## Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `knowledge_inventory.md` | Tracks all stored entries | Auto-updated on storage |
| `review_log.md` | Records review activities | Monthly manual updates |

## Knowledge Inventory

The `knowledge_inventory.md` file provides:

- **Summary Statistics** - Total entries by type and importance
- **Detailed Inventory** - Tables of all entries per type
- **Coverage Gaps** - Areas needing documentation
- **Growth Metrics** - Entries added over time
- **Deprecated Entries** - Superseded knowledge

### Automatic Updates

The inventory is updated automatically when:
- New knowledge is stored via validation scripts
- Entries are deprecated
- Bulk population scripts run

Update script: `validation/update_inventory.py`

### Manual Review Schedule

| Frequency | Review Focus |
|-----------|--------------|
| Weekly | Check for completeness, recent additions |
| Monthly | Verify all active projects have entries |
| Quarterly | Deprecate outdated entries, consolidate duplicates |

## Review Log

The `review_log.md` file tracks:

- Review dates and reviewers
- Issues found during review
- Actions taken (deprecations, updates)
- Coverage improvements

### Review Process

1. **Open inventory**: Check `knowledge_inventory.md`
2. **Identify gaps**: Look at Coverage Gaps section
3. **Verify accuracy**: Spot-check random entries
4. **Update deprecated**: Mark outdated entries
5. **Log review**: Record in `review_log.md`

## Customization

### Adapting for Your Project

1. **Update statistics categories** in `knowledge_inventory.md`:
   - Add/remove knowledge types
   - Adjust component lists
   - Modify importance levels

2. **Set review schedule** in `review_log.md`:
   - Adjust frequency based on team size
   - Add project-specific review criteria

3. **Configure auto-updates** in `validation/update_inventory.py`:
   - Modify which fields are tracked
   - Add custom metrics

### Example Customizations

```markdown
## By Component (Customized)

| Component | Count |
|-----------|-------|
| user-service | 5 |
| payment-api | 3 |
| notification-worker | 2 |
```

## Integration with BMAD

For BMAD workflows, tracking supports:

- **Sprint Planning**: Check what knowledge exists before planning
- **Dev Stories**: Reference existing patterns during implementation
- **Party Mode**: Quickly find agent capabilities
- **Post-Sprint**: Log new learnings from completed work

## Search Tips

To find entries in the inventory:

1. **Ctrl+F / Cmd+F** - Search within the file
2. **By unique_id** - Find specific entries
3. **By component** - Find all entries for a system
4. **By status** - Find active vs deprecated

For semantic search across actual content:
```python
mcp__qdrant__qdrant-find(query="your search query")
```

## Related Documentation

- [validation/](../validation/) - Scripts that update inventory
- [BMAD_INTEGRATION_RULES.md](../BMAD_INTEGRATION_RULES.md) - When to update tracking
- [CONFIGURATION.md](../CONFIGURATION.md) - Tracking configuration options
