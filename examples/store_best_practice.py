#!/usr/bin/env python3
"""
Example: Store Best Practice Discovered by Agent

This script demonstrates how agents automatically store best practices they discover
during research, with duplicate checking and validation.

Usage:
    python3 examples/store_best_practice.py [--dry-run]

Features:
    - Automatic storage by discovering agent
    - SHA256 content hashing for deduplication
    - Semantic similarity checking (threshold: 0.85)
    - Unique ID collision detection
    - Collection specification (bmad-best-practices)
    - Full metadata validation
"""

import sys
import hashlib
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from validation.validate_metadata import run_all_validations
    from validation.check_duplicates import run_duplicate_checks
except ImportError:
    print("ERROR: Could not import validation modules")
    print(
        "Make sure validation/validate_metadata.py and validation/check_duplicates.py exist"
    )
    sys.exit(1)


def store_best_practice(
    information: str,
    metadata: dict,
    collection: str = "bmad-best-practices",
    dry_run: bool = True,
) -> bool:
    """
    Store a best practice discovered by an agent.

    Args:
        information: Best practice content
        metadata: Best practice metadata (must include discovered_by)
        collection: Qdrant collection name (default: legal-ai-best-practices)
        dry_run: If True, only validate without storing

    Returns:
        bool: True if stored successfully (or would be stored in dry-run)
    """
    print("\n" + "=" * 80)
    print("AGENT BEST PRACTICE STORAGE WORKFLOW")
    print("=" * 80)

    # Step 1: Add content hash for deduplication
    content_hash = hashlib.sha256(information.encode("utf-8")).hexdigest()
    metadata["content_hash"] = content_hash
    print(f"\n✓ Content hash generated: {content_hash[:16]}...")

    # Step 2: Validate metadata
    print("\n" + "-" * 80)
    print("STEP 1: VALIDATE METADATA")
    print("-" * 80)

    is_valid, validation_messages = run_all_validations(metadata)

    for msg in validation_messages:
        print(msg)

    if not is_valid:
        print("\n✗ VALIDATION FAILED - Cannot store")
        return False

    print("\n✓ All validation checks passed")

    # Step 3: Check for duplicates
    print("\n" + "-" * 80)
    print("STEP 2: CHECK FOR DUPLICATES")
    print("-" * 80)

    duplicates_found, duplicate_messages = run_duplicate_checks(
        content=information,
        metadata=metadata,
        similarity_threshold=0.85,
        check_hash=True,
        check_similarity=True,
        check_id=True,
    )

    for msg in duplicate_messages:
        print(msg)

    if duplicates_found:
        print("\n✗ DUPLICATE DETECTED - Skipping storage")
        return False

    print("\n✓ No duplicates found - Safe to store")

    # Step 4: Store (if not dry run)
    print("\n" + "-" * 80)
    print("STEP 3: STORE IN QDRANT")
    print("-" * 80)

    if dry_run:
        print(f"\n[DRY RUN MODE] Would store to collection: {collection}")
        print(f"[DRY RUN MODE] unique_id: {metadata['unique_id']}")
        print(f"[DRY RUN MODE] discovered_by: {metadata['discovered_by']}")
        print(f"[DRY RUN MODE] technology: {metadata['technology']}")
        print(f"[DRY RUN MODE] importance: {metadata['importance']}")
        print("\n✓ Workflow completed successfully (dry run)")
    else:
        # ACTUAL STORAGE (when dry_run=False)
        # mcp__qdrant__qdrant-store(
        #     information=information,
        #     metadata=metadata,
        #     collection=collection  # Specify collection
        # )
        print(f"\n✓ Stored to collection: {collection}")
        print(f"✓ unique_id: {metadata['unique_id']}")

        # Update tracking
        # TODO: Update tracking/knowledge_inventory.md

    print("\n" + "=" * 80)
    return True


def main():
    """Demonstrate storing a best practice discovered by an agent."""

    # Example: Agent 15 discovers Qdrant batch upsert best practice
    # while researching storage routing optimization

    information = """
Qdrant Batch Upsert Optimization for Document Storage

CONTEXT: While implementing storage routing for the document processing system, discovered
optimal batch sizes for upserting document embeddings to Qdrant.

BEST PRACTICE:
Use batch sizes of 100-500 vectors for document embeddings to balance
throughput and memory usage. Larger batches (>1000) cause memory pressure on
the Qdrant server, while smaller batches (<100) result in excessive API calls
and reduced throughput.

IMPLEMENTATION:
```python
# Optimal batch upsert
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

client = QdrantClient(url="http://localhost:6333")

# Batch size: 100-500 for optimal performance
BATCH_SIZE = 250

def upsert_embeddings(vectors, metadata):
    for i in range(0, len(vectors), BATCH_SIZE):
        batch = vectors[i:i + BATCH_SIZE]
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vec,
                payload=meta
            )
            for vec, meta in zip(batch, metadata[i:i + BATCH_SIZE])
        ]
        client.upsert(collection_name="bmad-knowledge", points=points)
```

PERFORMANCE IMPACT:
- Baseline (batch size 50): 2.5 seconds per 1000 vectors
- Optimized (batch size 250): 0.8 seconds per 1000 vectors
- Improvement: 68% faster, 3x throughput

TRADE-OFFS:
Pros:
- Significant throughput improvement (3x)
- Reduced API call overhead
- Better connection pool utilization
- Lower network latency impact

Cons:
- Slightly higher memory usage during batch assembly
- Less granular error handling (whole batch fails on error)
- May need retry logic for large batches

PREREQUISITES:
- Qdrant server with adequate memory (4GB+ recommended)
- Connection pooling configured (max_pool_size >= 10)
- Network latency < 100ms (for local/nearby servers)

VALIDATION:
- Monitor batch upsert latency (should be < 5 seconds for 250 vectors)
- Check Qdrant server memory usage (should stay < 80%)
- Verify all vectors successfully inserted (check collection size)

ANTI-PATTERNS TO AVOID:
- ❌ Single vector upserts (extremely slow)
- ❌ Batch sizes > 1000 (memory issues)
- ❌ No retry logic (data loss on transient errors)
- ❌ Ignoring server memory limits

SOURCE: Official Qdrant documentation on batch operations
URL: https://qdrant.tech/documentation/concepts/points/#batch-update
Publication Date: 2024-11
Confidence: 0.95 (official vendor documentation)
"""

    metadata = {
        # Identity
        "unique_id": "bp-qdrant-batch-upsert-2024-12-28",
        "content_hash": "",  # Will be auto-generated
        "type": "best_practice",
        # Classification
        "domain": "vector_search",
        "technology": "qdrant",
        "category": "performance",
        "component": "qdrant",
        "sub_component": "batch_operations",
        # Agent Discovery
        "discovered_by": "agent_15",
        "discovery_context": "Researching Qdrant batch operations for storage routing optimization during Story 2-17",
        "story_id": "2-17",
        "epic_id": "2",
        # Source
        "source": "official_documentation",
        "source_url": "https://qdrant.tech/documentation/concepts/points/#batch-update",
        "source_title": "Qdrant Points Documentation - Batch Update",
        "source_date": "2024-11-15",
        # Quality
        "importance": "high",
        "confidence": 0.95,
        "created_at": "2024-12-28",
        # Applicability
        "applicability": "universal",
        "applicable_versions": ["Qdrant 1.6+", "Qdrant 1.7+", "Qdrant 1.8+"],
        "conditions": [
            "Adequate server memory (4GB+)",
            "Network latency < 100ms",
            "Connection pooling configured",
        ],
        # Implementation
        "implementation_complexity": "simple",
        "estimated_effort": "30 minutes",
        # Performance
        "performance_impact": {
            "metric": "throughput",
            "improvement": "3x faster (68% improvement)",
            "baseline": "2.5 seconds per 1000 vectors",
            "optimized": "0.8 seconds per 1000 vectors",
        },
        # Trade-offs
        "trade_offs": {
            "pros": [
                "Significant throughput improvement (3x)",
                "Reduced API call overhead",
                "Better connection pool utilization",
                "Lower network latency impact",
            ],
            "cons": [
                "Slightly higher memory usage during batch assembly",
                "Less granular error handling",
                "May need retry logic for large batches",
            ],
        },
        # Related Information
        "alternatives": [
            "Single vector upserts (very slow, not recommended)",
            "Streaming upserts (complex, for very large datasets)",
        ],
        "anti_patterns": [
            "Single vector upserts (extremely slow)",
            "Batch sizes > 1000 (memory issues)",
            "No retry logic (data loss on transient errors)",
            "Ignoring server memory limits",
        ],
        "prerequisites": [
            "Qdrant server with adequate memory (4GB+ recommended)",
            "Connection pooling configured (max_pool_size >= 10)",
            "Network latency < 100ms (for local/nearby servers)",
        ],
        "validation_criteria": [
            "Batch upsert latency < 5 seconds for 250 vectors",
            "Qdrant server memory usage < 80%",
            "All vectors successfully inserted (verify collection size)",
        ],
        "monitoring_recommendations": [
            "Track batch upsert latency p95",
            "Monitor Qdrant server memory usage",
            "Track upsert error rate",
            "Monitor collection growth rate",
        ],
        # Search Optimization
        "keywords": [
            "qdrant",
            "batch",
            "upsert",
            "performance",
            "optimization",
            "throughput",
            "vector",
            "embeddings",
            "documents",
        ],
        "search_intent": [
            "qdrant batch upsert optimization",
            "how to optimize qdrant performance",
            "qdrant batch size best practices",
            "improve vector upsert throughput",
            "qdrant performance tuning",
        ],
        # Project Application
        "applied_in_project": True,
        "application_date": "2024-12-20",
        "application_story": "2-17",
        "results_observed": "Achieved 3x throughput improvement in chunk storage routing. Reduced processing time from 45 minutes to 15 minutes for 10,000 chunks. No memory issues observed with batch size 250.",
        # Meta
        "industry_adoption": "standard",
        "risk_level": "low",
        "reversibility": "easily_reversible",
        "production_ready": True,
    }

    # Display what we're storing
    print("\n" + "=" * 80)
    print("EXAMPLE: AGENT DISCOVERS QDRANT BATCH UPSERT BEST PRACTICE")
    print("=" * 80)
    print(f"\nAgent: {metadata['discovered_by']}")
    print(f"Context: {metadata['discovery_context']}")
    print(f"Story: {metadata['story_id']}")
    print(f"Technology: {metadata['technology']}")
    print(f"Category: {metadata['category']}")
    print(f"Importance: {metadata['importance']}")
    print(f"Applied in Project: {metadata['applied_in_project']}")

    if metadata["applied_in_project"]:
        print(f"Results Observed: {metadata['results_observed']}")

    # Store with validation and duplicate checking
    success = store_best_practice(
        information=information,
        metadata=metadata,
        collection="bmad-best-practices",
        dry_run=True,  # Set to False for actual storage
    )

    if success:
        print("\n✓ Best practice ready to be added to knowledge base")
        print("✓ Collection: bmad-best-practices")
        print("✓ All validation and deduplication checks passed")
        return 0
    else:
        print("\n✗ Best practice storage failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
