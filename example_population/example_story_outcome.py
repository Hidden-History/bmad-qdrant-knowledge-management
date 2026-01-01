#!/usr/bin/env python3
"""
Example: Storing a Story Outcome

This script demonstrates how to store a completed story outcome
in the knowledge base with proper validation and deduplication.

Usage:
    python example_population/example_story_outcome.py
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


# Example story outcome - modify for your project
INFORMATION = """
Story 2-17: Implement Document Search API

WHAT WAS BUILT:
- RESTful API endpoint for document search (/api/v1/search)
- Query parser supporting natural language and structured queries
- Result ranking based on relevance and recency
- Pagination and filtering capabilities
- Search result highlighting

INTEGRATION POINTS:
- Search Service receives queries from API Gateway
- Queries vector database (Qdrant) for semantic search
- Falls back to keyword search for exact matches
- Returns results to frontend via REST API
- Logs search analytics to PostgreSQL

IMPLEMENTATION DETAILS:
- FastAPI endpoint with Pydantic validation
- Async handlers for non-blocking I/O
- Rate limiting: 100 requests/minute per user
- Response caching: 5-minute TTL for identical queries
- Maximum results per page: 50

COMMON ERRORS DISCOVERED:
1. Timeout on complex queries
   - Cause: Unbounded similarity search across all vectors
   - Solution: Added limit parameter and timeout configuration
   - Prevention: Always set max_results in search calls

2. Empty results for quoted phrases
   - Cause: Exact phrase matching not implemented
   - Solution: Added phrase detection in query parser
   - Prevention: Document query syntax in API docs

3. Slow response for first request
   - Cause: Model cold start for embedding generation
   - Solution: Pre-warm model on service startup
   - Prevention: Health check includes embedding test

TESTING:
- Unit tests: tests/unit/api/test_search_endpoint.py (23 tests)
- Integration tests: tests/integration/test_search_integration.py (12 tests)
- Load tests: tests/load/test_search_performance.py
- E2E coverage: Search flow tested end-to-end

PERFORMANCE RESULTS:
- Average latency: 180ms (p50), 450ms (p99)
- Throughput: 500 requests/second
- Relevance score: 0.87 MRR on test queries

FILES MODIFIED:
- src/api/routes/search.py (new)
- src/services/search_service.py (new)
- src/services/query_parser.py (new)
- src/models/search_models.py (new)
- tests/unit/api/test_search_endpoint.py (new)
- tests/integration/test_search_integration.py (new)
- docs/api/search.md (new)

CONFIGURATION ADDED:
- SEARCH_MAX_RESULTS: Maximum results per query (default: 100)
- SEARCH_TIMEOUT_MS: Query timeout in milliseconds (default: 5000)
- SEARCH_CACHE_TTL: Cache time-to-live in seconds (default: 300)

LESSONS LEARNED:
- Pre-warming embedding models significantly improves first-request latency
- Phrase detection in queries improves user experience
- Rate limiting is essential for production deployment
"""

METADATA = {
    "unique_id": "story-2-17-search-api-complete",
    "type": "story_outcome",
    "component": "api",
    "sub_component": "search",
    "importance": "high",
    "created_at": datetime.now().strftime("%Y-%m-%d"),
    "epic_id": "2",
    "story_id": "2-17",
    "affects": ["api", "search", "frontend", "analytics"],
    "keywords": [
        "search",
        "api",
        "rest",
        "query",
        "qdrant",
        "fastapi",
    ],
    "testing_status": "all_passing",
    "test_count": 35,
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

    # Check story-specific recommended fields
    if metadata.get("type") == "story_outcome":
        story_recommended = ["story_id", "epic_id"]
        for field in story_recommended:
            if field not in metadata:
                issues.append(f"Story outcome missing recommended field: {field}")

    # Check importance is valid
    valid_importance = ["critical", "high", "medium", "low"]
    if metadata.get("importance") not in valid_importance:
        issues.append(f"Invalid importance: {metadata.get('importance')}")

    return len(issues) == 0, issues


def main():
    """Main entry point for example script."""
    print("=" * 60)
    print("STORY OUTCOME STORAGE EXAMPLE")
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
    print(f"Epic ID: {METADATA['epic_id']}")
    print(f"Story ID: {METADATA['story_id']}")
    print(f"Component: {METADATA['component']}")
    print(f"Importance: {METADATA['importance']}")
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
    information="[story outcome content]",
    metadata={
        "unique_id": "%s",
        "type": "story_outcome",
        "story_id": "%s",
        "epic_id": "%s",
        ...
    }
)
""" % (METADATA['unique_id'], METADATA['story_id'], METADATA['epic_id']))

    return 0


if __name__ == "__main__":
    sys.exit(main())
