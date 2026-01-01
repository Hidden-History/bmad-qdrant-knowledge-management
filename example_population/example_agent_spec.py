#!/usr/bin/env python3
"""
Example: Storing an Agent Specification

This script demonstrates how to store an agent specification
in the knowledge base with proper validation and deduplication.

Usage:
    python example_population/example_agent_spec.py
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


# Example agent specification - modify for your project
INFORMATION = """
Agent: Document Classifier (Agent 03)

PURPOSE:
Analyzes document content and metadata to classify documents into appropriate
categories for downstream processing and storage routing.

INPUT:
- Document text content (string)
- Document metadata (dict): filename, source, creation_date, file_type
- Optional: Previous classifications for similar documents

OUTPUT:
- Classification result (dict):
  - primary_category: Main document category
  - sub_categories: List of applicable sub-categories
  - confidence: Float 0.0-1.0
  - reasoning: Explanation for classification
  - suggested_tags: Keywords for search optimization

DEPENDENCIES:
- NLP Service: For text analysis and entity extraction
- Configuration Service: For category definitions
- No upstream agent dependencies (can run independently)

INTEGRATION:
```python
from agents import DocumentClassifier

classifier = DocumentClassifier()
result = classifier.classify(
    content=document.text,
    metadata=document.metadata
)

# Result format:
# {
#     "primary_category": "technical_documentation",
#     "sub_categories": ["api_reference", "integration_guide"],
#     "confidence": 0.92,
#     "reasoning": "Contains API endpoints and code examples",
#     "suggested_tags": ["api", "rest", "integration"]
# }
```

CONFIGURATION:
- CLASSIFIER_MODEL: Model to use (default: "default")
- MIN_CONFIDENCE: Minimum confidence threshold (default: 0.7)
- MAX_CATEGORIES: Maximum sub-categories to return (default: 5)

COMMON ERRORS:
1. Empty content error
   - Cause: Document has no extractable text
   - Solution: Check document extraction upstream
   - Prevention: Add content validation before classification

2. Low confidence results
   - Cause: Document doesn't match known categories
   - Solution: Review category definitions or add new categories
   - Prevention: Implement fallback category for edge cases

3. Timeout on large documents
   - Cause: Document exceeds processing limits
   - Solution: Implement chunking for large documents
   - Prevention: Set MAX_CONTENT_LENGTH configuration

TESTING:
- Unit tests: tests/unit/agents/test_classifier.py
- Integration tests: tests/integration/test_agent_03_integration.py
- Test fixtures: tests/fixtures/classification_samples/

PERFORMANCE:
- Average latency: 150ms per document
- Throughput: ~400 documents/minute
- Memory usage: ~500MB with model loaded
"""

METADATA = {
    "unique_id": "agent-03-document-classifier-spec",
    "type": "agent_spec",
    "agent_id": "03",
    "agent_name": "document_classifier",
    "component": "agents",
    "sub_component": "classification",
    "importance": "critical",
    "created_at": datetime.now().strftime("%Y-%m-%d"),
    "dependencies": [],  # No upstream agent dependencies
    "integration_points": ["nlp_service", "config_service", "storage_router"],
    "common_errors": [
        "empty_content",
        "low_confidence",
        "timeout_large_docs",
    ],
    "keywords": [
        "classifier",
        "document",
        "categorization",
        "nlp",
        "agent",
    ],
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
        issues.append(f"Invalid type: {metadata.get('type')}")

    # Check agent-specific required fields
    if metadata.get("type") == "agent_spec":
        agent_required = ["agent_id", "agent_name"]
        for field in agent_required:
            if field not in metadata:
                issues.append(f"Agent spec missing: {field}")

    # Check importance is valid
    valid_importance = ["critical", "high", "medium", "low"]
    if metadata.get("importance") not in valid_importance:
        issues.append(f"Invalid importance: {metadata.get('importance')}")

    return len(issues) == 0, issues


def main():
    """Main entry point for example script."""
    print("=" * 60)
    print("AGENT SPECIFICATION STORAGE EXAMPLE")
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
    print(f"Agent ID: {METADATA['agent_id']}")
    print(f"Agent Name: {METADATA['agent_name']}")
    print(f"Importance: {METADATA['importance']}")
    print(f"Dependencies: {METADATA['dependencies']}")
    print()
    print("Content Preview:")
    print("-" * 40)
    print(INFORMATION[:500] + "..." if len(INFORMATION) > 500 else INFORMATION)
    print("-" * 40)
    print()

    print("READY TO STORE")
    print()
    print("To actually store this entry, use the MCP tool in Claude:")
    print("""
mcp__qdrant__qdrant-store(
    information="[agent spec content]",
    metadata={
        "unique_id": "%s",
        "type": "agent_spec",
        "agent_id": "%s",
        "agent_name": "%s",
        ...
    }
)
""" % (METADATA['unique_id'], METADATA['agent_id'], METADATA['agent_name']))

    return 0


if __name__ == "__main__":
    sys.exit(main())
