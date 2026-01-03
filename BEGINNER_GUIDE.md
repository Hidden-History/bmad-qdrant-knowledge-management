# The Complete BMAD + Qdrant Knowledge Management Guide

## A Step-by-Step Guide for Beginners

This guide teaches you how to build a **token-efficient AI memory system** by combining the **BMAD Method** (an AI-driven development framework) with **Qdrant** (a vector database). By the end, your AI agents will retrieve only the information they need—saving tokens and reducing confusion.

---

## Table of Contents

1. [What Problem Are We Solving?](#1-what-problem-are-we-solving)
2. [Prerequisites & Requirements](#2-prerequisites--requirements)
3. [Understanding the Core Concepts](#3-understanding-the-core-concepts)
4. [Step 1: Installing Qdrant](#4-step-1-installing-qdrant)
5. [Step 2: Installing the Qdrant Python Client](#5-step-2-installing-the-qdrant-python-client)
6. [Step 3: Creating Your First Collection](#6-step-3-creating-your-first-collection)
7. [Step 4: Setting Up Multitenancy](#7-step-4-setting-up-multitenancy)
8. [Step 5: Creating the Payload Index](#8-step-5-creating-the-payload-index)
9. [Step 6: The Atomic Shard Data Structure](#9-step-6-the-atomic-shard-data-structure)
10. [Step 7: Storing Data (Upserting Points)](#10-step-7-storing-data-upserting-points)
11. [Step 8: Searching with Tenant Isolation](#11-step-8-searching-with-tenant-isolation)
12. [Step 9: Complete Python Script](#12-step-9-complete-python-script)
13. [Step 10: Agent Search Rules](#13-step-10-agent-search-rules)
14. [Step 11: Workflow & Role Mapping](#14-step-11-workflow--role-mapping)
15. [Step 12: Verification & Testing](#15-step-12-verification--testing)
16. [Troubleshooting Guide](#16-troubleshooting-guide)
17. [Advanced: Tiered Multitenancy (v1.16+)](#17-advanced-tiered-multitenancy-v116)
18. [Reference Links](#18-reference-links)

---

## 1. What Problem Are We Solving?

### The Token Problem

When AI agents search a standard "flat" memory system, they often retrieve **everything**—relevant and irrelevant data alike. This causes:

- **Token waste**: Your AI's context window fills up with useless information
- **Confusion**: The AI may hallucinate or give contradictory answers
- **Slow responses**: More data = more processing time
- **Higher costs**: More tokens = more API costs

### The Solution: "Digital Filing Drawers"

We create a system where:

1. Every piece of information is **tagged** with metadata (project, story, type)
2. The AI **only opens the drawer it needs** for the current task
3. Irrelevant data is **completely ignored** at the database level

This can reduce token usage by **90% or more** for large projects.

---

## 2. Prerequisites & Requirements

Before starting, ensure you have:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Docker | 20.10+ | `docker --version` |
| Python | 3.8+ | `python --version` |
| pip | Latest | `pip --version` |
| 8GB+ RAM | - | - |

### Optional but Recommended

- **BMAD Method** for structured project management: `npx bmad-method@alpha install`
- An AI coding assistant (Claude, Cursor, Windsurf, etc.)

---

## 3. Understanding the Core Concepts

### What is Qdrant?

Qdrant is a **vector database**—it stores data as mathematical vectors (embeddings) that represent the meaning of text. This allows for **semantic search** (finding similar meanings) rather than just keyword matching.

### What is Multitenancy?

**Multitenancy** means multiple "tenants" (users, projects, stories) share the same database, but their data is logically separated. Think of it like an apartment building—everyone lives in the same building, but you can only access your own apartment.

### What is BMAD?

**BMAD** (Build More, Architect Dreams) is an AI-driven agile development framework with 21 specialized agents and 50+ workflows. It breaks projects into "atomic" pieces that are perfect for our filing system.

### Key Terminology

| Term | Meaning |
|------|---------|
| **Collection** | A database table in Qdrant |
| **Point** | A single record (vector + payload) |
| **Vector** | Mathematical representation of text (embedding) |
| **Payload** | Metadata attached to a vector |
| **Tenant** | A logical partition (project, story, user) |
| **HNSW** | The indexing algorithm Qdrant uses for fast search |

---

## 4. Step 1: Installing Qdrant

### Option A: Docker (Recommended for Beginners)

Open your terminal and run:

```bash
# Pull the latest Qdrant image
docker pull qdrant/qdrant

# Run Qdrant on port 6333 (REST API) and 6334 (gRPC)
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

**What this does:**
- Downloads Qdrant
- Starts it on ports 6333 and 6334
- Saves data to `./qdrant_storage` so it persists

### Option B: Docker Compose (For Production)

Create a file named `docker-compose.yml`:

```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
```

Then run:

```bash
docker-compose up -d
```

### Verify Installation

Open your browser and go to: `http://localhost:6333/dashboard`

You should see the Qdrant Web UI. If you see it, Qdrant is running!

---

## 5. Step 2: Installing the Qdrant Python Client

Install the required Python packages:

```bash
pip install qdrant-client sentence-transformers
```

**What these do:**
- `qdrant-client`: Official Python library to interact with Qdrant
- `sentence-transformers`: Library to convert text into vectors (embeddings)

### Test the Connection

Create a file named `test_connection.py`:

```python
from qdrant_client import QdrantClient

# Connect to local Qdrant
client = QdrantClient(host="localhost", port=6333)

# Check connection
print("Collections:", client.get_collections())
print("✅ Connected to Qdrant successfully!")
```

Run it:

```bash
python test_connection.py
```

---

## 6. Step 3: Creating Your First Collection

A **collection** is like a database table. We'll create one optimized for multitenancy.

### The Configuration Explained

```python
from qdrant_client import QdrantClient, models

client = QdrantClient(host="localhost", port=6333)

# Create a multitenant-optimized collection
client.create_collection(
    collection_name="bmad_memories",
    vectors_config=models.VectorParams(
        size=384,  # Must match your embedding model's output size
        distance=models.Distance.COSINE  # How similarity is measured
    ),
    hnsw_config=models.HnswConfigDiff(
        payload_m=16,  # Edges per node for filtered search (tenant-specific)
        m=0,           # ⚠️ DISABLES global search - only tenant-filtered search works
    ),
)

print("✅ Collection 'bmad_memories' created!")
```

### ⚠️ CRITICAL WARNING: Understanding `m=0`

Setting `m=0` **completely disables global search**. This means:

✅ **DO use `m=0` if:** You will ALWAYS search with a tenant filter (e.g., `context_id`)

❌ **DO NOT use `m=0` if:** You ever need to search across ALL tenants at once

If you need both tenant-specific AND global search, use this instead:

```python
hnsw_config=models.HnswConfigDiff(
    payload_m=16,
    m=16,  # Allows global search (slower for tenant queries)
),
```

---

## 7. Step 4: Setting Up Multitenancy

Multitenancy isolates each tenant's data so searches are fast and targeted.

### Understanding the Metadata Structure

Every piece of data you store needs these **Metadata IDs**:

| Field | Purpose | Example |
|-------|---------|---------|
| `project_id` | Separates different projects/clients | `"Project-Alpha"` |
| `context_id` | **THE MAIN TENANT ID** - separates stories/tasks | `"STORY-042"` |
| `node_type` | Categorizes content type | `"requirement"`, `"summary"`, `"task"` |

**The `context_id` is the most important tag.** It determines which "drawer" the data goes into.

---

## 8. Step 5: Creating the Payload Index

The **payload index** tells Qdrant which field to use for tenant isolation. This is crucial for performance.

```python
from qdrant_client import QdrantClient, models

client = QdrantClient(host="localhost", port=6333)

# Create tenant-optimized index for context_id
client.create_payload_index(
    collection_name="bmad_memories",
    field_name="context_id",
    field_schema=models.KeywordIndexParams(
        type=models.KeywordIndexType.KEYWORD,
        is_tenant=True,  # ⬅️ CRITICAL: Optimizes storage for tenant isolation
    ),
)

print("✅ Tenant index created for 'context_id'!")
```

### What `is_tenant=True` Does

When you set `is_tenant=True`:

1. **Storage optimization**: Vectors from the same tenant are stored physically close together on disk
2. **Faster reads**: Sequential disk reads instead of random access
3. **Better caching**: Related data is cached together

This parameter is available in **Qdrant v1.11.0+**.

---

## 9. Step 6: The Atomic Shard Data Structure

In BMAD methodology, we break documents into **atomic shards**—small, focused pieces of information. Each shard has a vector (embedding) and a payload (metadata).

### The Complete Shard Structure

```python
shard = {
    "id": "unique-uuid-123",           # Unique identifier
    "vector": [0.1, 0.2, ...],          # Embedding (384 or 1536 floats)
    "payload": {
        "project_id": "Project-Alpha",  # Which project
        "context_id": "STORY-042",      # Which story/task (TENANT ID)
        "node_type": "requirement",     # What type of content
        "content": "The system must...", # Actual text content
        "version": 1,                   # For tracking updates
        "created_at": "2025-01-03",     # Timestamp
        "agent": "analyst"              # Which agent created it
    }
}
```

### Node Types for BMAD Workflows

| Node Type | Description | Created By |
|-----------|-------------|------------|
| `summary` | High-level overview | Analyst, PM |
| `requirement` | Specific requirement | PM, Analyst |
| `spec` | Technical specification | Architect |
| `task_step` | Implementation step | Developer |
| `code_logic` | Code explanation | Developer |
| `test_case` | Test scenario | QA, Test Architect |
| `design` | UX/UI design notes | UX Designer |

---

## 10. Step 7: Storing Data (Upserting Points)

Now let's store actual data with embeddings.

### Step-by-Step Process

```python
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import uuid

# Initialize clients
client = QdrantClient(host="localhost", port=6333)
encoder = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dimensional embeddings

def create_and_store_shard(content, project_id, context_id, node_type):
    """Create an atomic shard and store it in Qdrant."""
    
    # Generate embedding from content
    vector = encoder.encode(content).tolist()
    
    # Create the point
    point = models.PointStruct(
        id=str(uuid.uuid4()),  # Unique ID
        vector=vector,          # The embedding
        payload={
            "project_id": project_id,
            "context_id": context_id,
            "node_type": node_type,
            "content": content,
            "version": 1
        }
    )
    
    # Store in Qdrant
    client.upsert(
        collection_name="bmad_memories",
        points=[point]
    )
    
    return point.id

# Example: Store a requirement
doc_id = create_and_store_shard(
    content="The system must allow users to reset passwords via email link within 5 minutes.",
    project_id="Project-Alpha",
    context_id="STORY-042",
    node_type="requirement"
)

print(f"✅ Stored document with ID: {doc_id}")
```

### Batch Upload (More Efficient)

```python
def batch_store_shards(shards_data):
    """Store multiple shards at once for better performance."""
    
    points = []
    for shard in shards_data:
        vector = encoder.encode(shard["content"]).tolist()
        points.append(models.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=shard
        ))
    
    client.upsert(
        collection_name="bmad_memories",
        points=points
    )
    
    return len(points)

# Example batch upload
shards = [
    {
        "project_id": "Project-Alpha",
        "context_id": "STORY-042",
        "node_type": "requirement",
        "content": "Users must receive email confirmation within 30 seconds.",
        "version": 1
    },
    {
        "project_id": "Project-Alpha",
        "context_id": "STORY-042",
        "node_type": "task_step",
        "content": "Implement SMTP integration with SendGrid API.",
        "version": 1
    },
    {
        "project_id": "Project-Alpha",
        "context_id": "STORY-043",  # Different story!
        "node_type": "summary",
        "content": "User authentication flow using OAuth2.",
        "version": 1
    }
]

count = batch_store_shards(shards)
print(f"✅ Stored {count} shards!")
```

---

## 11. Step 8: Searching with Tenant Isolation

Here's where the magic happens—searching **only within a specific tenant**.

### Basic Tenant-Filtered Search

```python
def search_within_context(query_text, context_id, limit=3, node_type=None):
    """
    Search for relevant content within a specific context (tenant).
    
    Args:
        query_text: What you're searching for
        context_id: The tenant/story ID to search within
        limit: Maximum results (keep low to save tokens!)
        node_type: Optional filter for specific content types
    """
    
    # Convert query to embedding
    query_vector = encoder.encode(query_text).tolist()
    
    # Build filter conditions
    must_conditions = [
        models.FieldCondition(
            key="context_id",
            match=models.MatchValue(value=context_id)
        )
    ]
    
    # Optional: filter by node type
    if node_type:
        must_conditions.append(
            models.FieldCondition(
                key="node_type",
                match=models.MatchValue(value=node_type)
            )
        )
    
    # Execute search
    results = client.query_points(
        collection_name="bmad_memories",
        query=query_vector,
        query_filter=models.Filter(must=must_conditions),
        limit=limit,
        with_payload=True
    )
    
    return results.points

# Example: Search only in STORY-042
results = search_within_context(
    query_text="password reset email",
    context_id="STORY-042",
    limit=3
)

for point in results:
    print(f"Score: {point.score:.3f}")
    print(f"Type: {point.payload['node_type']}")
    print(f"Content: {point.payload['content'][:100]}...")
    print("---")
```

### Important: Why We Limit Results

Setting a **low limit** (3-5) is critical because:

1. **Token savings**: Each result adds to your AI's context window
2. **Relevance**: Top results are usually the most relevant
3. **Speed**: Fewer results = faster response

**Rule of thumb**: Start with `limit=3`. Only increase if the AI can't find what it needs.

---

## 12. Step 9: Complete Python Script

Here's everything in one ready-to-use script:

```python
"""
BMAD + Qdrant Knowledge Management System
Complete setup and usage script for beginners.
"""

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import uuid
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

COLLECTION_NAME = "bmad_memories"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions
VECTOR_SIZE = 384

# ============================================
# INITIALIZATION
# ============================================

print("🚀 Initializing BMAD Knowledge Management System...")

# Connect to Qdrant
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
print(f"✅ Connected to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")

# Load embedding model
encoder = SentenceTransformer(EMBEDDING_MODEL)
print(f"✅ Loaded embedding model: {EMBEDDING_MODEL}")

# ============================================
# SETUP FUNCTIONS
# ============================================

def setup_collection():
    """Create the collection with multitenancy optimization."""
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if COLLECTION_NAME in collection_names:
        print(f"⚠️  Collection '{COLLECTION_NAME}' already exists. Skipping creation.")
        return
    
    # Create collection
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE
        ),
        hnsw_config=models.HnswConfigDiff(
            payload_m=16,
            m=0,  # Disable global search for tenant optimization
        ),
    )
    print(f"✅ Created collection: {COLLECTION_NAME}")
    
    # Create tenant index
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="context_id",
        field_schema=models.KeywordIndexParams(
            type=models.KeywordIndexType.KEYWORD,
            is_tenant=True,
        ),
    )
    print("✅ Created tenant index on 'context_id'")
    
    # Create additional indexes for filtering
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="project_id",
        field_schema=models.KeywordIndexParams(
            type=models.KeywordIndexType.KEYWORD,
        ),
    )
    print("✅ Created index on 'project_id'")
    
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="node_type",
        field_schema=models.KeywordIndexParams(
            type=models.KeywordIndexType.KEYWORD,
        ),
    )
    print("✅ Created index on 'node_type'")

# ============================================
# DATA OPERATIONS
# ============================================

def store_shard(content: str, project_id: str, context_id: str, 
                node_type: str, agent: str = "system") -> str:
    """
    Store a single atomic shard in the knowledge base.
    
    Returns the generated UUID.
    """
    vector = encoder.encode(content).tolist()
    point_id = str(uuid.uuid4())
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[models.PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "project_id": project_id,
                "context_id": context_id,
                "node_type": node_type,
                "content": content,
                "agent": agent,
                "version": 1,
                "created_at": datetime.now().isoformat()
            }
        )]
    )
    
    return point_id


def search_context(query: str, context_id: str, limit: int = 3,
                   node_type: str = None) -> list:
    """
    Search within a specific context (tenant).
    
    Args:
        query: Search query text
        context_id: The story/task ID to search within
        limit: Maximum results (default 3 for token efficiency)
        node_type: Optional filter for specific types
    
    Returns:
        List of matching points with scores
    """
    query_vector = encoder.encode(query).tolist()
    
    must_conditions = [
        models.FieldCondition(
            key="context_id",
            match=models.MatchValue(value=context_id)
        )
    ]
    
    if node_type:
        must_conditions.append(
            models.FieldCondition(
                key="node_type",
                match=models.MatchValue(value=node_type)
            )
        )
    
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=models.Filter(must=must_conditions),
        limit=limit,
        with_payload=True
    )
    
    return results.points


def get_context_summary(context_id: str) -> list:
    """Get summary nodes first (incremental loading pattern)."""
    return search_context(
        query="overview summary main purpose",
        context_id=context_id,
        limit=1,
        node_type="summary"
    )

# ============================================
# DEMO / TEST
# ============================================

def run_demo():
    """Demonstrate the system with sample data."""
    
    print("\n📝 Loading demo data...")
    
    # Story A data
    store_shard(
        content="STORY-A is about implementing a user authentication system with OAuth2 and JWT tokens.",
        project_id="Demo-Project",
        context_id="STORY-A",
        node_type="summary",
        agent="analyst"
    )
    
    store_shard(
        content="The authentication system must support Google and GitHub OAuth providers.",
        project_id="Demo-Project",
        context_id="STORY-A",
        node_type="requirement",
        agent="pm"
    )
    
    store_shard(
        content="JWT tokens must expire after 24 hours and refresh tokens after 7 days.",
        project_id="Demo-Project",
        context_id="STORY-A",
        node_type="requirement",
        agent="pm"
    )
    
    # Story B data (different tenant!)
    store_shard(
        content="STORY-B covers the payment processing integration with Stripe API.",
        project_id="Demo-Project",
        context_id="STORY-B",
        node_type="summary",
        agent="analyst"
    )
    
    store_shard(
        content="Payment system must support credit cards, Apple Pay, and Google Pay.",
        project_id="Demo-Project",
        context_id="STORY-B",
        node_type="requirement",
        agent="pm"
    )
    
    print("✅ Demo data loaded!\n")
    
    # Test tenant isolation
    print("=" * 50)
    print("🔍 TEST: Search for 'authentication' in STORY-A")
    print("=" * 50)
    
    results_a = search_context(
        query="authentication login OAuth",
        context_id="STORY-A",
        limit=3
    )
    
    for point in results_a:
        print(f"  Score: {point.score:.3f} | Type: {point.payload['node_type']}")
        print(f"  Content: {point.payload['content'][:80]}...")
        print()
    
    print("=" * 50)
    print("🔍 TEST: Search for 'authentication' in STORY-B")
    print("   (Should return NO auth results - only payment!)")
    print("=" * 50)
    
    results_b = search_context(
        query="authentication login OAuth",
        context_id="STORY-B",
        limit=3
    )
    
    for point in results_b:
        print(f"  Score: {point.score:.3f} | Type: {point.payload['node_type']}")
        print(f"  Content: {point.payload['content'][:80]}...")
        print()
    
    if not any("OAuth" in p.payload["content"] for p in results_b):
        print("✅ SUCCESS! Tenant isolation working correctly!")
        print("   STORY-B search did NOT return STORY-A data.")
    else:
        print("❌ FAILURE! Tenant isolation may be broken.")

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    setup_collection()
    run_demo()
```

**Save this as `bmad_qdrant_setup.py` and run:**

```bash
python bmad_qdrant_setup.py
```

---

## 13. Step 10: Agent Search Rules

Add these rules to your AI agent's system prompt or configuration to enforce proper search behavior:

### System Prompt Addition

```markdown
## BMAD Knowledge Management Rules

When interacting with the Qdrant `bmad_memories` collection, you MUST follow these rules:

### Required Behavior

1. **ALWAYS filter by context_id**: Every search MUST include a `context_id` filter for the current Story or Task you're working on.

2. **NEVER perform global searches**: Do not search without a tenant filter. Global searches are disabled for token efficiency.

3. **Use incremental loading**:
   - First, request `summary` nodes to get an overview
   - Only request `requirement`, `task_step`, or `code_logic` if the summary doesn't provide enough information
   - This saves tokens by loading information progressively

4. **Limit results**: Never set `limit` higher than 5 unless explicitly required for analysis. Start with 3.

5. **Filter by node_type when possible**: If you only need requirements, filter for `node_type: requirement`.

### Example Correct Search

```python
# ✅ CORRECT: Filtered by context_id and limited results
search_context(
    query="user authentication flow",
    context_id="STORY-042",  # Always specify!
    limit=3,
    node_type="requirement"  # Optional but recommended
)
```

### Example Incorrect Search

```python
# ❌ WRONG: No context_id filter (will fail or return nothing)
client.query_points(
    collection_name="bmad_memories",
    query=vector,
    limit=100  # Too high!
)
```
```

---

## 14. Step 11: Workflow & Role Mapping

Assign **drawer ownership** to different BMAD agents to prevent conflicts:

| Agent | Primary Node Types | Access Pattern |
|-------|-------------------|----------------|
| **Analyst** | `summary`, `brief` | Read/Write |
| **PM** | `requirement`, `acceptance_criteria` | Read/Write |
| **Architect** | `spec`, `architecture`, `module` | Read/Write |
| **Developer** | `task_step`, `code_logic` | Read (requirements), Write (tasks) |
| **UX Designer** | `design`, `wireframe` | Read/Write |
| **QA / Test Architect** | `test_case`, `bug` | Read (requirements), Write (tests) |
| **Scrum Master** | All types | Read only |

### Implementation

```python
# Define agent permissions
AGENT_PERMISSIONS = {
    "analyst": {
        "write": ["summary", "brief", "research"],
        "read": ["*"]  # Can read everything
    },
    "pm": {
        "write": ["requirement", "acceptance_criteria", "epic"],
        "read": ["*"]
    },
    "architect": {
        "write": ["spec", "architecture", "module", "interface"],
        "read": ["*"]
    },
    "developer": {
        "write": ["task_step", "code_logic", "implementation"],
        "read": ["requirement", "spec", "architecture", "task_step"]
    },
    "qa": {
        "write": ["test_case", "bug", "test_result"],
        "read": ["requirement", "spec", "task_step"]
    }
}

def can_write(agent: str, node_type: str) -> bool:
    """Check if an agent can write a specific node type."""
    perms = AGENT_PERMISSIONS.get(agent, {})
    allowed = perms.get("write", [])
    return node_type in allowed

def can_read(agent: str, node_type: str) -> bool:
    """Check if an agent can read a specific node type."""
    perms = AGENT_PERMISSIONS.get(agent, {})
    allowed = perms.get("read", [])
    return "*" in allowed or node_type in allowed
```

---

## 15. Step 12: Verification & Testing

### The Isolation Test

This is the most important test—verify that tenants are truly isolated:

```python
def run_isolation_test():
    """
    Test that tenant isolation is working correctly.
    
    SUCCESS: Searching in STORY-A returns only STORY-A content
    FAILURE: Searching in STORY-A returns ANY content from STORY-B
    """
    
    print("🧪 Running Isolation Test...\n")
    
    # Store test data in STORY-A
    store_shard(
        content="UNIQUE_STRING_ALPHA_123: This is only in Story A",
        project_id="Test",
        context_id="ISOLATION-TEST-A",
        node_type="test"
    )
    
    # Store test data in STORY-B
    store_shard(
        content="UNIQUE_STRING_BETA_456: This is only in Story B",
        project_id="Test",
        context_id="ISOLATION-TEST-B",
        node_type="test"
    )
    
    # Search in STORY-A for content that should only be in STORY-B
    results = search_context(
        query="UNIQUE_STRING_BETA_456",
        context_id="ISOLATION-TEST-A",
        limit=5
    )
    
    # Check results
    found_beta_content = any(
        "BETA_456" in p.payload.get("content", "") 
        for p in results
    )
    
    if found_beta_content:
        print("❌ ISOLATION FAILED!")
        print("   Content from STORY-B was returned when searching STORY-A")
        return False
    else:
        print("✅ ISOLATION PASSED!")
        print("   STORY-A search correctly excluded STORY-B content")
        return True

# Run the test
run_isolation_test()
```

### Health Check Script

```python
def health_check():
    """Verify the system is configured correctly."""
    
    print("🏥 Running Health Check...\n")
    checks = []
    
    # 1. Check Qdrant connection
    try:
        client.get_collections()
        checks.append(("Qdrant Connection", True, "Connected"))
    except Exception as e:
        checks.append(("Qdrant Connection", False, str(e)))
    
    # 2. Check collection exists
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in collections:
        checks.append(("Collection Exists", True, COLLECTION_NAME))
    else:
        checks.append(("Collection Exists", False, "Not found"))
    
    # 3. Check indexes
    collection_info = client.get_collection(COLLECTION_NAME)
    indexed_fields = list(collection_info.payload_schema.keys())
    
    required_indexes = ["context_id", "project_id", "node_type"]
    for idx in required_indexes:
        if idx in indexed_fields:
            checks.append((f"Index: {idx}", True, "Indexed"))
        else:
            checks.append((f"Index: {idx}", False, "Missing"))
    
    # Print results
    print("=" * 50)
    for check_name, passed, detail in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {detail}")
    print("=" * 50)
    
    all_passed = all(c[1] for c in checks)
    if all_passed:
        print("\n✅ All health checks passed!")
    else:
        print("\n❌ Some checks failed. Please review configuration.")
    
    return all_passed

health_check()
```

---

## 16. Troubleshooting Guide

### Problem: "Collection already exists" Error

**Solution:**
```python
# Delete and recreate
client.delete_collection(COLLECTION_NAME)
setup_collection()
```

### Problem: Search Returns Empty Results

**Possible causes:**
1. **Wrong `context_id`**: Double-check the exact string
2. **No data stored**: Verify data was uploaded
3. **`m=0` with no filter**: You MUST include `context_id` filter

**Debug:**
```python
# Check if collection has data
info = client.get_collection(COLLECTION_NAME)
print(f"Total points: {info.points_count}")

# List all unique context_ids
results = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=100,
    with_payload=True
)
context_ids = set(p.payload.get("context_id") for p in results[0])
print(f"Context IDs: {context_ids}")
```

### Problem: Slow Search Performance

**Solutions:**
1. Ensure `is_tenant=True` is set on the index
2. Reduce `limit` to 3-5
3. Add `node_type` filter when possible

### Problem: Embeddings Don't Match

**Cause:** Using different embedding models for storing vs searching

**Solution:** Always use the same model:
```python
# Use consistent model everywhere
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
encoder = SentenceTransformer(EMBEDDING_MODEL)
```

### Problem: "No module named 'qdrant_client'" Error

**Solution:**
```bash
pip install qdrant-client sentence-transformers --upgrade
```

---

## 17. Advanced: Tiered Multitenancy (v1.16+)

For large-scale systems where some tenants grow much bigger than others, Qdrant v1.16 introduced **Tiered Multitenancy**.

### When to Use It

- You have a few large tenants and many small ones
- Large tenants need dedicated resources
- You want to dynamically promote growing tenants

### How It Works

1. Small tenants share a "fallback" shard
2. Large tenants get promoted to dedicated shards
3. Routing is automatic based on shard existence

### Basic Setup

```python
# Create collection with custom sharding
client.create_collection(
    collection_name="tiered_memories",
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    shard_number=1,
    sharding_method=models.ShardingMethod.CUSTOM
)

# Create fallback shard for small tenants
client.create_shard_key("tiered_memories", "default")

# When a tenant grows large, promote to dedicated shard
client.create_shard_key("tiered_memories", "big_tenant_1")
```

For full documentation, see: [Qdrant Tiered Multitenancy](https://qdrant.tech/documentation/guides/multitenancy/#tiered-multitenancy)

---

## 18. Reference Links

### Official Documentation

| Resource | URL |
|----------|-----|
| Qdrant Multitenancy Guide | https://qdrant.tech/documentation/guides/multitenancy/ |
| Qdrant Quick Start | https://qdrant.tech/documentation/quickstart/ |
| Qdrant Python Client | https://python-client.qdrant.tech/ |
| BMAD Method GitHub | https://github.com/bmad-code-org/BMAD-METHOD |
| BMAD Installation | `npx bmad-method@alpha install` |
| Sentence Transformers | https://www.sbert.net/ |

### Embedding Models

| Model | Dimensions | Speed | Quality |
|-------|------------|-------|---------|
| `all-MiniLM-L6-v2` | 384 | Fast | Good |
| `all-mpnet-base-v2` | 768 | Medium | Better |
| `text-embedding-3-small` (OpenAI) | 1536 | API | Excellent |

### Community Resources

| Resource | URL |
|----------|-----|
| Qdrant Discord | https://discord.gg/qdrant |
| BMAD Discord | https://discord.gg/gk8jAdXWmj |
| Qdrant GitHub Issues | https://github.com/qdrant/qdrant/issues |

---

## Summary Checklist

Before deploying, verify:

- [ ] Qdrant is running (`http://localhost:6333/dashboard`)
- [ ] Collection created with `payload_m=16` and `m=0` (or `m=16` for global search)
- [ ] Tenant index created with `is_tenant=True` on `context_id`
- [ ] Embedding model loaded and consistent
- [ ] Agent search rules configured
- [ ] Isolation test passes
- [ ] Health check passes

**Congratulations!** You now have a token-efficient AI memory system that keeps your agents focused and your costs low. 🎉

---

*Guide Version: 1.0 | Last Updated: January 2026*
*Compatible with: Qdrant 1.11+, Python 3.8+, BMAD Method v6*
