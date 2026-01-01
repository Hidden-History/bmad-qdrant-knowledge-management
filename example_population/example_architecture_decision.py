#!/usr/bin/env python3
"""
Example: Storing an Architecture Decision

This script demonstrates how to store an architecture decision
in the knowledge base with proper validation and deduplication.

Usage:
    python example_population/example_architecture_decision.py
"""

import sys
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    KNOWLEDGE_COLLECTION,
    PROJECT_NAME,
    ALLOWED_TYPES,
)


# Example architecture decision - modify for your project
INFORMATION = """
Architecture Decision: Microservices vs Monolith

DECISION:
Adopt microservices architecture for the document processing pipeline.

JUSTIFICATION:
1. Independent scaling - Each service can scale based on its specific load
2. Technology flexibility - Services can use different tech stacks as needed
3. Fault isolation - Failure in one service doesn't cascade to others
4. Team autonomy - Different teams can own and deploy services independently

TRADE-OFFS:
PROS:
- Better scalability and performance tuning
- Easier to maintain smaller codebases
- Can deploy changes without affecting entire system

CONS:
- Increased operational complexity
- Network latency between services
- Data consistency challenges
- More infrastructure to manage

IMPACTS:
- Requires container orchestration (Kubernetes/Docker Compose)
- Need for service mesh or API gateway
- Distributed logging and monitoring required
- Database per service pattern recommended

ALTERNATIVES CONSIDERED:
1. Monolith - Simpler but doesn't scale well
2. Modular monolith - Middle ground, rejected due to deployment coupling
3. Serverless - Rejected due to cold start latency concerns

IMPLEMENTATION:
- Phase 1: Extract document ingestion as standalone service
- Phase 2: Separate processing pipeline from storage
- Phase 3: Add dedicated search service
"""

METADATA = {
    "unique_id": f"arch-decision-microservices-{datetime.now().strftime('%Y%m%d')}",
    "type": "architecture_decision",
    "component": "infrastructure",
    "sub_component": "system_architecture",
    "importance": "critical",
    "created_at": datetime.now().strftime("%Y-%m-%d"),
    "breaking_change": True,
    "affects": ["deployment", "scaling", "monitoring", "development"],
    "keywords": [
        "microservices",
        "architecture",
        "scalability",
        "deployment",
        "containers",
    ],
    "rationale": "Enable independent scaling and team autonomy",
    "project": PROJECT_NAME,
}


def generate_content_hash(content: str) -> str:
    """Generate SHA256 hash for deduplication."""
    return hashlib.sha256(content.encode()).hexdigest()


def validate_metadata(metadata: dict) -> tuple[bool, list]:
    """Validate metadata against requirements."""
    issues = []

    # Check required fields
    required = ["unique_id", "type", "component", "importance", "created_at"]
    for field in required:
        if field not in metadata:
            issues.append(f"Missing required field: {field}")

    # Check type is valid
    if metadata.get("type") not in ALLOWED_TYPES:
        issues.append(f"Invalid type: {metadata.get('type')}. Must be one of: {ALLOWED_TYPES}")

    # Check importance is valid
    valid_importance = ["critical", "high", "medium", "low"]
    if metadata.get("importance") not in valid_importance:
        issues.append(f"Invalid importance: {metadata.get('importance')}")

    return len(issues) == 0, issues


def main():
    """Main entry point for example script."""
    print("=" * 60)
    print("ARCHITECTURE DECISION STORAGE EXAMPLE")
    print("=" * 60)
    print()

    # Add content hash for deduplication
    METADATA["content_hash"] = generate_content_hash(INFORMATION)

    # Validate metadata
    is_valid, issues = validate_metadata(METADATA)

    if not is_valid:
        print("VALIDATION FAILED:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("Metadata Validation: PASSED")
    print()
    print(f"Collection: {KNOWLEDGE_COLLECTION}")
    print(f"Unique ID: {METADATA['unique_id']}")
    print(f"Type: {METADATA['type']}")
    print(f"Component: {METADATA['component']}")
    print(f"Importance: {METADATA['importance']}")
    print(f"Breaking Change: {METADATA['breaking_change']}")
    print()
    print("Content Preview:")
    print("-" * 40)
    print(INFORMATION[:500] + "..." if len(INFORMATION) > 500 else INFORMATION)
    print("-" * 40)
    print()

    # In a real implementation, you would store to Qdrant here:
    #
    # from qdrant_client import QdrantClient
    # client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    #
    # # Generate embedding (example with sentence-transformers)
    # from sentence_transformers import SentenceTransformer
    # model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    # embedding = model.encode(INFORMATION).tolist()
    #
    # # Upsert to collection
    # client.upsert(
    #     collection_name=KNOWLEDGE_COLLECTION,
    #     points=[{
    #         "id": str(uuid.uuid4()),
    #         "vector": embedding,
    #         "payload": {"information": INFORMATION, **METADATA}
    #     }]
    # )

    print("READY TO STORE")
    print()
    print("To actually store this entry, uncomment the Qdrant client code")
    print("and ensure your Qdrant server is running.")
    print()
    print("Or use the MCP tool directly in Claude:")
    print("""
mcp__qdrant__qdrant-store(
    information="[content here]",
    metadata={
        "unique_id": "%s",
        "type": "architecture_decision",
        ...
    }
)
""" % METADATA['unique_id'])

    return 0


if __name__ == "__main__":
    sys.exit(main())
