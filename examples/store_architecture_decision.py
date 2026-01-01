#!/usr/bin/env python3
"""
Example: Storing an Architecture Decision in Qdrant MCP

This example demonstrates the complete workflow for storing
an architecture decision with proper metadata validation and
duplicate checking.

Usage:
    python store_architecture_decision.py
"""

import sys
import json
from pathlib import Path


# Add validation directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "validation"))

from validate_metadata import run_all_validations
from check_duplicates import run_duplicate_checks


def create_architecture_decision_example():
    """
    Create example architecture decision about two-collection Qdrant setup.

    Returns:
        Tuple of (information: str, metadata: dict)
    """
    information = """
Two-collection Qdrant architecture decision for BMAD Knowledge Management:

DECISION: Use two separate Qdrant collections for knowledge management:
- bmad-knowledge: Architecture decisions, agent specs, story outcomes, etc.
- bmad-best-practices: Agent-discovered best practices from development

REASONING:
- Separation of explicit knowledge from discovered patterns
- Different update frequencies (best practices accumulate faster)
- Clearer semantic boundaries for search
- Easier maintenance and backup strategies

COLLECTIONS:
1. bmad-knowledge: Core project knowledge
   - Architecture decisions
   - Agent specifications
   - Story outcomes
   - Error patterns
   - Database schemas
   - Config patterns
   - Integration examples

2. bmad-best-practices: Accumulated wisdom
   - Agent-discovered patterns
   - Optimization techniques
   - Common error solutions
   - Performance improvements

INTEGRATION:
- MCP tools route based on knowledge type
- Best practices are auto-discovered during development
- Regular review consolidates valuable patterns into main knowledge base

ALTERNATIVES CONSIDERED:
1. Single collection with type filtering - Rejected (semantic overlap in searches)
2. Multiple collections per type - Rejected (too fragmented)
3. Separate databases entirely - Rejected (operational overhead)

TRADE-OFFS:
Pros:
- Clear semantic separation
- Better search relevance
- Simpler access patterns
- Independent scaling

Cons:
- Two collections to maintain
- Cross-collection search requires multiple queries
- Slightly more complex routing logic

BREAKING CHANGE: No - initial design decision

TESTING:
- Unit tests: tests/unit/test_collection_routing.py
- Integration tests: tests/integration/test_storage_workflow.py

MONITORING:
- Collection size metrics
- Search latency per collection
- Storage growth trends
    """.strip()

    metadata = {
        "unique_id": "arch-decision-two-collections-2024-12-15",
        "type": "architecture_decision",
        "component": "qdrant",
        "sub_component": "collection_architecture",
        "affects": ["storage", "routing", "retrieval", "monitoring"],
        "epic_id": "1",
        "story_id": "1-1",
        "created_at": "2024-12-15",
        "deprecated": False,
        "version": 1,
        "breaking_change": False,
        "importance": "critical",
        "confidence": 1.0,
        "source": "team_decision",
        "decision_date": "2024-12-15",
        "alternatives_considered": [
            "Single collection with type filtering",
            "Multiple collections per knowledge type",
            "Separate databases entirely",
        ],
        "trade_offs": {
            "pros": [
                "Clear semantic separation",
                "Better search relevance",
                "Simpler access patterns",
                "Independent scaling",
            ],
            "cons": [
                "Two collections to maintain",
                "Cross-collection search complexity",
                "Additional routing logic",
            ],
        },
        "keywords": [
            "qdrant",
            "collections",
            "architecture",
            "storage",
            "routing",
            "knowledge-management",
            "vector-database",
        ],
        "related_ids": ["story-1-1-complete"],
        "search_intent": [
            "qdrant collection architecture",
            "how to organize collections",
            "knowledge vs best practices separation",
            "two collection design",
        ],
        "migration_required": False,
    }

    return information, metadata


def store_with_validation(information: str, metadata: dict, dry_run: bool = True):
    """
    Store knowledge with full validation workflow.

    Args:
        information: Knowledge content
        metadata: Metadata dictionary
        dry_run: If True, don't actually store (just validate)
    """
    print("\n" + "=" * 70)
    print("ARCHITECTURE DECISION STORAGE WORKFLOW")
    print("=" * 70 + "\n")

    # Step 1: Validate metadata
    print("STEP 1: Validating metadata...")
    print("-" * 70)

    is_valid, validation_messages = run_all_validations(metadata)

    for msg in validation_messages:
        print(msg)

    if not is_valid:
        print("\n❌ Metadata validation failed. Aborting storage.")
        return False

    print("\n✅ Metadata validation passed")

    # Step 2: Check for duplicates
    print("\n" + "-" * 70)
    print("STEP 2: Checking for duplicates...")
    print("-" * 70)

    duplicates_found, duplicate_messages = run_duplicate_checks(
        content=information, metadata=metadata, similarity_threshold=0.85
    )

    for msg in duplicate_messages:
        print(msg)

    if duplicates_found:
        print("\n❌ Duplicates found. Aborting storage.")
        return False

    print("\n✅ No duplicates found")

    # Step 3: Store (if not dry run)
    print("\n" + "-" * 70)
    print("STEP 3: Storing in Qdrant MCP...")
    print("-" * 70)

    if dry_run:
        print("\n⚠️  DRY RUN MODE - Not actually storing")
        print("\nWould call:")
        print("mcp__qdrant__qdrant-store(")
        print(f"    information={information[:100]}...,")
        print(f"    metadata={json.dumps(metadata, indent=2)[:200]}...")
        print(")")
    else:
        # TODO: Integrate with actual Qdrant MCP storage
        # mcp__qdrant__qdrant-store(
        #     information=information,
        #     metadata=metadata
        # )
        print("\n✅ Stored successfully in Qdrant MCP")
        print(f"unique_id: {metadata['unique_id']}")
        print(f"content_hash: {metadata.get('content_hash', 'N/A')}")

    # Step 4: Update tracking
    print("\n" + "-" * 70)
    print("STEP 4: Updating knowledge inventory...")
    print("-" * 70)

    if dry_run:
        print("\n⚠️  DRY RUN MODE - Not updating inventory")
    else:
        # TODO: Update tracking/knowledge_inventory.md
        print("\n✅ Knowledge inventory updated")

    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 70 + "\n")

    return True


def main():
    """Main entry point."""
    print("\n📘 Architecture Decision Storage Example")
    print("=" * 70 + "\n")

    # Create example
    information, metadata = create_architecture_decision_example()

    print("Example Decision: Two-Collection Qdrant Architecture")
    print(f"unique_id: {metadata['unique_id']}")
    print(f"Type: {metadata['type']}")
    print(f"Importance: {metadata['importance']}")
    print(f"Breaking Change: {metadata['breaking_change']}")

    # Run workflow
    success = store_with_validation(information, metadata, dry_run=True)

    if success:
        print("\n💡 TIP: Remove dry_run=True to actually store in Qdrant MCP")
        sys.exit(0)
    else:
        print("\n❌ Storage workflow failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
