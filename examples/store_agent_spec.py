#!/usr/bin/env python3
"""
Example: Storing an Agent Specification in Qdrant MCP

This example demonstrates storing detailed agent specification
with integration points, dependencies, and common usage patterns.

Usage:
    python store_agent_spec.py
"""

import sys
from pathlib import Path


# Add validation directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "validation"))

from validate_metadata import run_all_validations
from check_duplicates import run_duplicate_checks


def create_agent_spec_example():
    """
    Create example agent specification for a document classifier agent.

    Returns:
        Tuple of (information: str, metadata: dict)
    """
    information = """
Agent: Document Classifier (Agent 03)

PURPOSE:
Classifies documents into appropriate categories for downstream processing
and storage routing in the knowledge management system.

INPUT:
- document: Document object with text content
- metadata: dict with document metadata
  - filename: str
  - source: str
  - created_at: str

OUTPUT:
- classification: dict
  - category: str (technical, reference, guide, api_docs, tutorial)
  - confidence: float (0.0-1.0)
  - subcategories: list[str]
  - suggested_tags: list[str]

DEPENDENCIES:
None - this agent can run independently as the first step in a pipeline.

Dependency chain:
1. Document is submitted → Agent 03 classifies
2. Classification result → routes to appropriate collection
3. Qdrant receives document → stores with classification metadata

INTEGRATION POINTS:
- Qdrant Collections: Routes to bmad-knowledge or bmad-best-practices
- MCP Tools: Integrates with qdrant-store for storage
- Metadata: Updates document metadata with classification

CLASSIFICATION LOGIC:
Technical Documentation:
  - category: 'technical'
  - Examples: Architecture decisions, system design docs

Reference Materials:
  - category: 'reference'
  - Examples: API documentation, configuration guides

Guides & Tutorials:
  - category: 'guide'
  - Examples: How-to guides, tutorials, walkthroughs

Story Outcomes:
  - category: 'story_outcome'
  - Examples: Completed feature documentation, implementation notes

VALIDATION:
- Ensures classification category is in allowed list
- Validates confidence score is between 0.0 and 1.0
- Logs classification decision for review

COMMON ERRORS:
1. ERROR: "Document too short for classification"
   CAUSE: Document has less than 50 characters
   SOLUTION: Ensure documents meet minimum length requirements

2. ERROR: "Unknown document format"
   CAUSE: Document is not in a recognized format
   SOLUTION: Convert to supported format (text, markdown)

3. ERROR: "Classification confidence too low"
   CAUSE: Document doesn't match any category well
   SOLUTION: Manual review required, or add new category

CONFIGURATION:
Environment variables:
- CLASSIFICATION_MIN_CONFIDENCE=0.7
- CLASSIFICATION_DEFAULT_CATEGORY=general
- CLASSIFICATION_LOG_LEVEL=INFO

TESTING:
Unit tests:
- tests/unit/agents/test_classifier.py
  - test_category_detection()
  - test_confidence_calculation()
  - test_tag_extraction()

Integration tests:
- tests/integration/test_classifier_integration.py
  - test_full_classification_workflow()
  - test_storage_routing()

PERFORMANCE:
- Average latency: 100-200ms per document
- Throughput: 50-100 documents/second
- Memory usage: ~500MB with model loaded

ERROR HANDLING:
- Retry logic: 3 attempts with exponential backoff
- Fallback: If classification fails, use 'general' category
- Logging: All classification decisions logged for review

MONITORING:
- Prometheus metrics: classifier_latency, classification_confidence
- Dashboard: "Classification Performance"
- Alerts: low_confidence_rate > 10%

IMPLEMENTATION FILES:
- src/agents/classifier/classifier.py
- src/agents/classifier/validation.py
- src/agents/classifier/categories.py
    """.strip()

    metadata = {
        "unique_id": "agent-03-classifier-spec",
        "type": "agent_spec",
        "agent_id": "agent_03",
        "agent_name": "document_classifier",
        "component": "agents",
        "sub_component": "classification",
        "dependencies": [],
        "dependents": ["storage_router"],
        "integration_points": [
            "qdrant_knowledge",
            "qdrant_best_practices",
            "mcp_storage_tools",
        ],
        "epic_id": "1",
        "story_id": "1-5",
        "created_at": "2024-12-20",
        "deprecated": False,
        "version": 1,
        "breaking_change": False,
        "importance": "critical",
        "confidence": 1.0,
        "source": "implementation",
        "common_errors": [
            "Document too short for classification",
            "Unknown document format",
            "Classification confidence too low",
        ],
        "input_schema": {
            "document": {"type": "object", "required": ["content", "metadata"]},
            "metadata": {
                "type": "object",
                "required": ["filename"],
            },
        },
        "output_schema": {
            "category": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "subcategories": {"type": "array", "items": {"type": "string"}},
        },
        "configuration": {
            "CLASSIFICATION_MIN_CONFIDENCE": "0.7",
            "CLASSIFICATION_DEFAULT_CATEGORY": "general",
            "CLASSIFICATION_LOG_LEVEL": "INFO",
        },
        "test_files": [
            "tests/unit/agents/test_classifier.py",
            "tests/integration/test_classifier_integration.py",
        ],
        "implementation_files": [
            "src/agents/classifier/classifier.py",
            "src/agents/classifier/validation.py",
            "src/agents/classifier/categories.py",
        ],
        "keywords": [
            "classification",
            "categorization",
            "document",
            "agent-03",
            "routing",
            "nlp",
        ],
        "related_ids": [
            "arch-decision-two-collections-2024-12-15",
            "story-1-5-complete",
        ],
        "search_intent": [
            "how to classify documents",
            "document classification agent",
            "category detection",
            "agent 03 usage",
        ],
        "performance_characteristics": {
            "average_latency_ms": 150,
            "throughput": "50-100 documents/second",
            "resource_usage": "Moderate CPU, 500MB memory",
        },
        "error_handling": "Retry 3x with exponential backoff, fallback to general category",
        "retry_logic": True,
    }

    return information, metadata


def main():
    """Main entry point."""
    print("\n🤖 Agent Specification Storage Example")
    print("=" * 70 + "\n")

    # Create example
    information, metadata = create_agent_spec_example()

    print("Example Agent: Agent 03 (document_classifier)")
    print(f"unique_id: {metadata['unique_id']}")
    print(f"Dependencies: {', '.join(metadata['dependencies'])}")
    print(f"Integration Points: {len(metadata['integration_points'])} connections")

    # Validate metadata
    print("\n" + "-" * 70)
    print("Validating metadata...")
    print("-" * 70 + "\n")

    is_valid, messages = run_all_validations(metadata)

    for msg in messages:
        print(msg)

    if not is_valid:
        print("\n❌ Validation failed")
        sys.exit(1)

    print("\n✅ Validation passed")

    # Check duplicates
    print("\n" + "-" * 70)
    print("Checking for duplicates...")
    print("-" * 70)

    duplicates_found, dup_messages = run_duplicate_checks(
        content=information, metadata=metadata, similarity_threshold=0.85
    )

    for msg in dup_messages:
        print(msg)

    if duplicates_found:
        print("\n❌ Duplicates found")
        sys.exit(1)

    print("\n✅ No duplicates")

    # Ready to store
    print("\n" + "=" * 70)
    print("✅ READY TO STORE")
    print("=" * 70)
    print("\nTo actually store, call:")
    print("mcp__qdrant__qdrant-store(")
    print("    information=information,")
    print("    metadata=metadata")
    print(")")

    sys.exit(0)


if __name__ == "__main__":
    main()
