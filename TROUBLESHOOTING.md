# Troubleshooting Guide

> Solutions to common issues

## TL;DR

Most issues are connection problems or missing configuration. Check Qdrant is running and `.env` is configured.

## Quick Fixes

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| "Connection refused" | Qdrant not running | `docker start qdrant` |
| "Collection not found" | Not initialized | Run `create_collections.py` |
| "API key invalid" | Wrong key | Check `.env` file |
| "MCP not working" | Config error | Restart Claude, check JSON |
| "Duplicate detected" | Entry exists | Search first, update if needed |

## Connection Issues

### "Connection refused" Error

**Symptom:** Scripts fail with connection refused error.

**Solutions:**

1. **Check if Qdrant is running:**
   ```bash
   docker ps | grep qdrant
   ```

2. **Start Qdrant if not running:**
   ```bash
   docker start qdrant
   # or start fresh:
   docker run -d -p 6333:6333 --name qdrant qdrant/qdrant
   ```

3. **Verify connection:**
   ```bash
   curl http://localhost:6333/health
   ```

4. **Check URL in .env:**
   ```bash
   cat .env | grep QDRANT_URL
   ```

### "Unauthorized" Error

**Symptom:** API requests fail with 401 error.

**Solutions:**

1. **For local Qdrant:** Remove API key from config (not needed for local)

2. **For Qdrant Cloud:** Verify API key in `.env`:
   ```bash
   # Check key is set
   cat .env | grep QDRANT_API_KEY
   ```

3. **Regenerate API key** in Qdrant Cloud dashboard if needed.

## Collection Issues

### "Collection not found" Error

**Symptom:** Storage or search fails because collection doesn't exist.

**Solutions:**

1. **Create collections:**
   ```bash
   python scripts/create_collections.py
   ```

2. **Verify collection exists:**
   ```bash
   python scripts/create_collections.py --check-only
   ```

3. **Check collection name matches config:**
   ```bash
   cat .env | grep QDRANT_KNOWLEDGE_COLLECTION
   ```

### Collections Have Wrong Settings

**Symptom:** Vector dimension mismatch or other config issues.

**Solutions:**

1. **Delete and recreate:**
   ```bash
   # Use Qdrant API or dashboard to delete
   curl -X DELETE "http://localhost:6333/collections/bmad-knowledge"

   # Recreate
   python scripts/create_collections.py
   ```

2. **Verify embedding dimension matches:**
   ```bash
   cat .env | grep EMBEDDING_DIMENSION
   ```

## MCP Server Issues

### MCP Not Connecting

**Symptom:** Claude can't access Qdrant MCP tools.

**Solutions:**

1. **Restart Claude Code/Desktop** - MCP loads on startup

2. **Check MCP configuration syntax:**
   - Valid JSON (no trailing commas)
   - Correct paths and URLs
   - Proper quoting

3. **Verify MCP server installed:**
   ```bash
   npx -y @modelcontextprotocol/server-qdrant --help
   ```

4. **Check Claude logs** for MCP errors

### MCP Commands Not Working

**Symptom:** MCP is connected but commands fail.

**Solutions:**

1. **Verify Qdrant URL** in MCP config matches running server

2. **Test Qdrant directly:**
   ```bash
   curl http://localhost:6333/collections
   ```

3. **Check collection name** in MCP config matches created collection

## Storage Issues

### "Duplicate detected" Error

**Symptom:** Can't store entry because similar one exists.

**Solutions:**

1. **Search for existing entry:**
   ```
   Search Qdrant for: "[your content keywords]"
   ```

2. **Update existing entry** instead of creating new

3. **Use different unique_id** if truly distinct

4. **Check deduplication threshold** in `.env`:
   ```bash
   SIMILARITY_THRESHOLD=0.85  # Lower = more strict
   ```

### "Validation failed" Error

**Symptom:** Entry rejected due to metadata issues.

**Solutions:**

1. **Check required fields:**
   - `unique_id` - Unique identifier
   - `type` - One of: architecture_decision, agent_spec, story_outcome, error_pattern, database_schema, config_pattern, integration_example, best_practice
   - `component` - System component name
   - `importance` - critical, high, medium, or low
   - `created_at` - ISO date format

2. **Verify type is valid:**
   ```python
   from config import ALLOWED_TYPES
   print(ALLOWED_TYPES)
   ```

3. **Check content length:**
   - Minimum: 100 characters
   - Maximum: 50,000 characters

### Content Not Found in Search

**Symptom:** Stored content doesn't appear in search results.

**Solutions:**

1. **Wait for indexing** - May take a few seconds

2. **Try different search terms** - Semantic search, not exact match

3. **Check correct collection:**
   - `best_practice` type goes to best-practices collection
   - Other types go to knowledge collection

4. **Verify entry exists:**
   ```bash
   python scripts/qdrant_cleanup.py --validate-entry "your-unique-id"
   ```

## Script Issues

### Import Errors

**Symptom:** Scripts fail with import errors.

**Solutions:**

1. **Install dependencies:**
   ```bash
   pip install qdrant-client python-dotenv
   ```

2. **Run from project root:**
   ```bash
   cd /path/to/bmad-qdrant-knowledge-management
   python scripts/create_collections.py
   ```

3. **Check Python version:**
   ```bash
   python --version  # Need 3.8+
   ```

### ".env not found" Warning

**Symptom:** Scripts warn about missing .env file.

**Solutions:**

1. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Set environment variables directly:**
   ```bash
   export QDRANT_URL=http://localhost:6333
   ```

## Performance Issues

### Slow Searches

**Symptom:** Search queries take too long.

**Solutions:**

1. **Use more specific search terms**

2. **Check collection size:**
   ```bash
   python scripts/create_collections.py --check-only
   ```

3. **Consider Qdrant Cloud** for better performance at scale

### Slow Storage

**Symptom:** Storing entries takes too long.

**Solutions:**

1. **Use batch operations** for multiple entries

2. **Check network latency** to Qdrant server

3. **Reduce content size** if very large

## Getting Help

If you can't resolve an issue:

1. **Check existing issues** on GitHub
2. **Create new issue** with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version)
3. **Include relevant logs**

## Useful Commands

```bash
# Check Qdrant health
curl http://localhost:6333/health

# List collections
curl http://localhost:6333/collections

# Check configuration
python -c "from config import validate_config; print(validate_config())"

# Audit collections
python scripts/qdrant_cleanup.py --audit

# Validate specific entry
python scripts/qdrant_cleanup.py --validate-entry "unique-id"
```
