#!/usr/bin/env python3
"""
Example: Common Search Patterns for Qdrant MCP Knowledge Base

Demonstrates effective search queries for different use cases:
- Finding past solutions
- Checking architecture constraints
- Understanding agent usage
- Discovering error solutions

Usage:
    python search_patterns.py
"""

from typing import List


def demo_search_pattern(
    use_case: str, query: str, why: str, example_results: List[str]
):
    """
    Demonstrate a search pattern.

    Args:
        use_case: What the user is trying to do
        query: The search query to use
        why: Explanation of why this query works
        example_results: Expected result types
    """
    print("\n" + "=" * 70)
    print(f"USE CASE: {use_case}")
    print("=" * 70 + "\n")

    print(f'QUERY: "{query}"')
    print("\nWHY THIS WORKS:")
    print(f"  {why}")

    print("\nEXPECTED RESULTS:")
    for i, result in enumerate(example_results, 1):
        print(f"  {i}. {result}")

    print("\nTO EXECUTE:")
    print(f'  results = mcp__qdrant__qdrant-find(query="{query}")')


def main():
    """Demonstrate common search patterns."""
    print("\n📖 Qdrant MCP Knowledge Base - Common Search Patterns")
    print("=" * 70)

    # Pattern 1: Finding past solutions
    demo_search_pattern(
        use_case="Before implementing a storage feature",
        query="storage routing collection assignment",
        why="Short, focused keywords about the domain. Vector search finds semantically similar past work.",
        example_results=[
            "story-2-17-complete (Story outcome with implementation details)",
            "agent-03-spec (Agent specification with integration points)",
            "arch-decision-two-collections (Architecture decision)",
        ],
    )

    # Pattern 2: Checking architecture constraints
    demo_search_pattern(
        use_case="Verify collection architecture before making changes",
        query="qdrant collection architecture constraints",
        why="Targets architectural decisions with specific technical details.",
        example_results=[
            "arch-decision-two-collections (Design rationale, trade-offs)",
            "config-qdrant-connection (Connection configuration pattern)",
            "error-qdrant-connection (Common error if config wrong)",
        ],
    )

    # Pattern 3: Understanding agent dependencies
    demo_search_pattern(
        use_case="Need to know which agents to call before storage",
        query="agent dependencies integration order",
        why="Focuses on agent integration and sequencing. Finds agent specs and integration examples.",
        example_results=[
            "agent-03-spec (Shows classification as first step)",
            "integration-agent-storage (Integration example)",
            "error-classification-not-found (Common error when called out of order)",
        ],
    )

    # Pattern 4: Solving Docker errors
    demo_search_pattern(
        use_case="Getting 'connection refused' error from Qdrant container",
        query="docker qdrant connection refused",
        why="Error-focused query with specific symptom. Finds error patterns and solutions.",
        example_results=[
            "error-docker-qdrant-connection (Exact match with solution)",
            "config-qdrant-connection (Configuration that might help)",
            "arch-decision-docker-setup (Context about container setup)",
        ],
    )

    # Pattern 5: Finding implementation patterns
    demo_search_pattern(
        use_case="How to implement agent database integration",
        query="agent database integration logging pattern",
        why="Combines multiple concepts. Finds integration examples and related patterns.",
        example_results=[
            "integration-agent-postgres-logging (Integration example)",
            "agent-03-spec (Shows database integration)",
            "schema-routing-log-postgres (Database schema details)",
        ],
    )

    # Pattern 6: Checking for known errors
    demo_search_pattern(
        use_case="Encountered embedding dimension mismatch",
        query="embedding dimension mismatch vector",
        why="Uses exact error message keywords. Finds documented error patterns.",
        example_results=[
            "error-embedding-dimension-mismatch (Error pattern with fix)",
            "config-embedding-model (Model configuration)",
            "agent-03-spec (Validation logic that prevents this)",
        ],
    )

    # Pattern 7: Understanding database schemas
    demo_search_pattern(
        use_case="Need to know structure of knowledge collection",
        query="knowledge collection schema metadata fields",
        why="Collection-specific query with metadata context. Finds schema documentation.",
        example_results=[
            "schema-bmad-knowledge (Complete collection definition)",
            "story-1-1-complete (When fields were added)",
            "agent-03-spec (Which agents use this collection)",
        ],
    )

    # Pattern 8: Finding configuration examples
    demo_search_pattern(
        use_case="How to configure Qdrant connection properly",
        query="qdrant connection configuration environment",
        why="Configuration-focused with context about what system. Finds config patterns.",
        example_results=[
            "config-qdrant-connection (Connection configuration pattern)",
            "config.py (Shows required environment variables)",
            "error-qdrant-timeout (Common config mistake)",
        ],
    )

    # Search Best Practices
    print("\n" + "=" * 70)
    print("SEARCH BEST PRACTICES")
    print("=" * 70 + "\n")

    print("✅ DO:")
    print("  - Use 2-5 focused keywords")
    print("  - Include specific technical terms (collection names, agent IDs)")
    print("  - Combine domain + technical concepts (e.g., 'agent routing storage')")
    print("  - Use error message keywords for problem-solving")
    print("  - Be specific but not too verbose")

    print("\n❌ DON'T:")
    print("  - Write full sentences or questions")
    print("  - Use generic terms alone ('database', 'error', 'config')")
    print("  - Keyword dump (10+ words)")
    print("  - Include filler words ('how to', 'what is', 'I want to')")

    print("\n💡 EXAMPLES:")

    good_bad_examples = [
        ("✅ GOOD", "qdrant collection routing agent", "Short, focused, specific"),
        (
            "❌ BAD",
            "how do I use the agent to route documents to different qdrant collections based on classification",
            "Too long, conversational",
        ),
        (
            "✅ GOOD",
            "metadata schema knowledge collection fields",
            "Specific collection and attribute",
        ),
        ("❌ BAD", "database schema", "Too generic"),
        (
            "✅ GOOD",
            "docker container qdrant connection refused error",
            "Error symptom with context",
        ),
        ("❌ BAD", "not working", "Vague, no details"),
    ]

    for status, query, reason in good_bad_examples:
        print(f'\n  {status}: "{query}"')
        print(f"    → {reason}")

    # Advanced patterns
    print("\n" + "=" * 70)
    print("ADVANCED SEARCH PATTERNS")
    print("=" * 70 + "\n")

    print("1. METADATA FILTERING (when supported):")
    print("   query='qdrant collections', filter={'type': 'architecture_decision'}")

    print("\n2. TYPE-SPECIFIC SEARCHES:")
    print("   For agents: 'agent {id} spec integration dependencies'")
    print("   For errors: '{error symptom} {component} solution'")
    print("   For schema: '{collection name} schema metadata fields'")

    print("\n3. CROSS-REFERENCE SEARCHES:")
    print("   Find related by story: 'story 2-17 implementation outcomes'")
    print("   Find related by epic: 'epic 1 architecture decisions'")

    print("\n4. TIME-BASED (with metadata):")
    print("   Recent changes: filter={'created_at': '> 2024-12-01'}")
    print("   Deprecated: filter={'deprecated': True}")

    print("\n" + "=" * 70)
    print("✅ SEARCH PATTERNS GUIDE COMPLETE")
    print("=" * 70)

    print("\nTo execute these searches in your code:")
    print('  results = mcp__qdrant__qdrant-find(query="your search here")')
    print("\nFor best results:")
    print("  - Keep queries SHORT (2-5 keywords)")
    print("  - Use SPECIFIC technical terms")
    print("  - Focus on PROBLEM or CONCEPT, not full sentences")


if __name__ == "__main__":
    main()
