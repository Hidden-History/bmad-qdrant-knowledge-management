#!/usr/bin/env python3
"""
Create Qdrant Collections for Knowledge Management

Creates the two required collections:
1. Knowledge collection - Project-specific institutional memory (7 types)
2. Best practices collection - Agent-discovered best practices (1 type)

Configuration is loaded from config.py and can be customized via environment variables.

Usage:
    python3 scripts/create_collections.py
    python3 scripts/create_collections.py --check-only
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse

from config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    KNOWLEDGE_COLLECTION,
    BEST_PRACTICES_COLLECTION,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
    ALLOWED_TYPES,
)


# Collection definitions using configured names
COLLECTIONS = {
    KNOWLEDGE_COLLECTION: {
        "description": "Project-specific institutional memory",
        "types": [t for t in ALLOWED_TYPES if t != "best_practice"],
    },
    BEST_PRACTICES_COLLECTION: {
        "description": "Agent-discovered universal best practices",
        "types": ["best_practice"],
    },
}


def get_client():
    """Get Qdrant client with API key if available."""
    try:
        # Connect with API key if available
        if QDRANT_API_KEY:
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        else:
            client = QdrantClient(url=QDRANT_URL)

        # Test connection
        client.get_collections()
        return client
    except Exception as e:
        print(f"ERROR: Could not connect to Qdrant at {QDRANT_URL}")
        print(f"Details: {e}")
        print("\nMake sure Qdrant is running:")
        print("  docker ps | grep qdrant")
        print("\nCheck your .env file or environment variables:")
        print("  QDRANT_URL")
        print("  QDRANT_API_KEY (optional for local)")
        sys.exit(1)


def check_collections(client):
    """Check which collections already exist."""
    print("\n" + "=" * 80)
    print("CHECKING EXISTING COLLECTIONS")
    print("=" * 80 + "\n")

    try:
        collections = client.get_collections()
        existing = [col.name for col in collections.collections]

        if not existing:
            print("No collections found.")
            return set()

        print(f"Found {len(existing)} collection(s):")
        for name in existing:
            info = client.get_collection(name)
            print(f"  - {name}: {info.points_count} points, status: {info.status}")

        return set(existing)

    except Exception as e:
        print(f"ERROR: Could not list collections: {e}")
        return set()


def create_collection(client, name, description, types):
    """Create a single collection."""
    print(f"\n{'='*80}")
    print(f"CREATING COLLECTION: {name}")
    print(f"{'='*80}")
    print(f"\nDescription: {description}")
    print(f"Vector Size: {EMBEDDING_DIMENSION}")
    print("Distance Metric: Cosine")
    print(f"Knowledge Types: {len(types)}")
    for t in types:
        print(f"  - {t}")

    try:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=EMBEDDING_DIMENSION, distance=Distance.COSINE),
        )
        print(f"\n  Collection '{name}' created successfully")
        return True

    except UnexpectedResponse as e:
        if "already exists" in str(e).lower():
            print(f"\n  Collection '{name}' already exists")
            return False
        else:
            print(f"\n  ERROR: {e}")
            return False
    except Exception as e:
        print(f"\n  ERROR: {e}")
        return False


def verify_collections(client):
    """Verify collections were created correctly."""
    print("\n" + "=" * 80)
    print("VERIFYING COLLECTIONS")
    print("=" * 80 + "\n")

    success = True

    for name in COLLECTIONS.keys():
        try:
            info = client.get_collection(name)
            print(f"  {name}:")
            print(f"   Points: {info.points_count}")
            print(f"   Status: {info.status}")
        except Exception as e:
            print(f"  {name}: {e}")
            success = False

    return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create Qdrant collections for knowledge management"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check existing collections, don't create new ones",
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("QDRANT COLLECTION SETUP FOR KNOWLEDGE MANAGEMENT")
    print("=" * 80)
    print(f"\nQdrant URL: {QDRANT_URL}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Vector Size: {EMBEDDING_DIMENSION}")
    print(f"\nCollections to create:")
    print(f"  - {KNOWLEDGE_COLLECTION} (project knowledge)")
    print(f"  - {BEST_PRACTICES_COLLECTION} (best practices)")

    # Get client
    client = get_client()

    # Check existing collections
    existing = check_collections(client)

    if args.check_only:
        print("\n" + "=" * 80)
        print("CHECK COMPLETE (--check-only mode)")
        print("=" * 80)
        return 0

    # Create missing collections
    created_count = 0
    for name, config in COLLECTIONS.items():
        if name not in existing:
            if create_collection(client, name, config["description"], config["types"]):
                created_count += 1
        else:
            print(f"\n  Skipping '{name}' (already exists)")

    # Verify
    print("\n")
    if verify_collections(client):
        print("\n" + "=" * 80)
        print("  ALL COLLECTIONS READY")
        print("=" * 80)
        print(f"\nCreated: {created_count} new collection(s)")
        print(f"Total: {len(COLLECTIONS)} collection(s)")

        print("\n  NEXT STEPS:")
        print("\n1. Configure Qdrant MCP server in your Claude settings:")
        print("   See: CONFIGURATION.md")
        print("\n2. Start populating with knowledge:")
        print("   - Architecture decisions")
        print("   - Agent specifications")
        print("   - Story outcomes")
        print("\n3. Test storage workflow:")
        print("   python3 examples/store_architecture_decision.py")

        return 0
    else:
        print("\n" + "=" * 80)
        print("  VERIFICATION FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
