# Quickstart Guide

> Get Qdrant MCP Knowledge Management running in 15 minutes

## TL;DR

1. Start Qdrant: `docker run -p 6333:6333 qdrant/qdrant`
2. Copy `.env.example` to `.env`
3. Run: `python scripts/create_collections.py`
4. Configure Claude MCP settings
5. Start storing knowledge!

## Prerequisites Checklist

- [ ] Docker installed (or Qdrant Cloud account)
- [ ] Python 3.8+
- [ ] Claude Code or Claude Desktop
- [ ] pip (Python package manager)

## Step 1: Start Qdrant (2 minutes)

### Option A: Local Docker (Recommended for Development)

```bash
# Start Qdrant with persistent storage
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Verify it's running
curl http://localhost:6333/health
```

### Option B: Qdrant Cloud (Recommended for Production)

1. Create account at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a new cluster
3. Get your URL and API key
4. Update `.env` with cloud credentials

## Step 2: Configure Environment (2 minutes)

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your settings (most defaults are fine for local development)
# For Qdrant Cloud, update QDRANT_URL and QDRANT_API_KEY
```

Key settings to review:
- `QDRANT_URL` - Default `http://localhost:6333` for local
- `QDRANT_API_KEY` - Leave empty for local, required for cloud
- `QDRANT_KNOWLEDGE_COLLECTION` - Collection name (default: `bmad-knowledge`)

## Step 3: Install Dependencies (1 minute)

```bash
# Install qdrant-client
pip install qdrant-client

# Optional: Install python-dotenv for .env loading
pip install python-dotenv
```

## Step 4: Create Collections (1 minute)

```bash
# Check connection first
python scripts/create_collections.py --check-only

# Create the collections
python scripts/create_collections.py
```

Expected output:
```
================================================================================
QDRANT COLLECTION SETUP FOR KNOWLEDGE MANAGEMENT
================================================================================

Qdrant URL: http://localhost:6333
Embedding Model: sentence-transformers/all-MiniLM-L6-v2
Vector Size: 384

Collections to create:
  - bmad-knowledge (project knowledge)
  - bmad-best-practices (best practices)

...

  ALL COLLECTIONS READY
================================================================================
```

## Step 5: Configure Claude MCP (5 minutes)

### For Claude Code

Add to `~/.claude/settings.json`:

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

### For Claude Desktop

Add to your Claude Desktop MCP configuration:

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

### For Qdrant Cloud

```json
{
  "mcpServers": {
    "qdrant": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-qdrant"],
      "env": {
        "QDRANT_URL": "https://your-cluster-url.qdrant.io",
        "QDRANT_API_KEY": "your-api-key-here",
        "COLLECTION_NAME": "bmad-knowledge"
      }
    }
  }
}
```

## Step 6: Test It Works (4 minutes)

### Test Storage

In Claude, ask it to store something:

```
Store this in Qdrant:
Information: "Test entry - setting up knowledge management system"
Metadata: {"unique_id": "test-setup-20250101", "type": "config_pattern", "component": "setup", "importance": "low", "created_at": "2025-01-01"}
```

### Test Retrieval

Search for your test entry:

```
Search Qdrant for: "knowledge management setup"
```

You should see your test entry returned.

### Clean Up Test Entry

```bash
# Use the cleanup script to remove test entries
python scripts/qdrant_cleanup.py --delete --test-only --execute
```

## You're Done!

Your Qdrant MCP Knowledge Management system is ready. Here's what to do next:

### Immediate Next Steps

1. **Store your first real entry** - Document a recent architecture decision
2. **Read the usage guide** - [CONFIGURATION.md](CONFIGURATION.md) for customization
3. **Set up BMAD integration** - [BMAD_INTEGRATION_RULES.md](BMAD_INTEGRATION_RULES.md)

### Recommended First Entries

Start building your knowledge base with:
- Top 3 architecture decisions for your project
- Key database schemas
- Common error patterns you've encountered

### Daily Workflow

1. **Search before implementing** - Check for past solutions
2. **Store after completing** - Document outcomes and decisions
3. **Review monthly** - Clean up duplicates, deprecate outdated entries

## Troubleshooting

### "Connection refused" Error

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Start if not running
docker start qdrant
```

### "Collection not found" Error

```bash
# Create the collections
python scripts/create_collections.py
```

### MCP Server Not Working

1. Restart Claude Code/Desktop
2. Check MCP configuration syntax (valid JSON)
3. Verify Qdrant URL is accessible

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.
