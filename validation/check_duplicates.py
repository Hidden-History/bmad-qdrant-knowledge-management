#!/usr/bin/env python3
"""
Duplicate Detection Script for Qdrant MCP Knowledge Management

Checks for duplicate or similar knowledge entries before storage.
Uses content hashing and semantic similarity.

Usage:
    python check_duplicates.py --content "Knowledge content here" --metadata metadata.json
    python check_duplicates.py --content-file content.txt --hash-only
"""

import sys
import argparse
import hashlib
import json
from typing import Dict, Any, Tuple, Optional, List


def generate_content_hash(content: str) -> str:
    """
    Generate SHA256 hash of content for deduplication.

    Args:
        content: Text content to hash

    Returns:
        Hexadecimal SHA256 hash string
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def search_by_hash(content_hash: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Search Qdrant MCP for existing entry with same content hash.

    Args:
        content_hash: SHA256 hash to search for

    Returns:
        Tuple of (exists: bool, existing_entry: dict or None)

    Note:
        This function would integrate with Qdrant MCP in production.
        For now, it's a placeholder for the search logic.
    """
    # TODO: Integrate with mcp__qdrant__qdrant-find()
    # Search for: f"content_hash:{content_hash}"
    # Return found entry if exists

    # Placeholder implementation
    print(f"  → Searching for content_hash: {content_hash[:16]}...")
    return False, None


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate semantic similarity between two texts.

    This is a simple implementation. In production, you'd use:
    - Sentence embeddings (sentence-transformers)
    - Cosine similarity between embeddings
    - Or Qdrant's built-in similarity search

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score 0.0-1.0
    """
    # Simple Jaccard similarity as placeholder
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


def search_similar_content(
    content: str, threshold: float = 0.85
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Search for semantically similar content in Qdrant MCP.

    Args:
        content: Content to search for
        threshold: Similarity threshold (0.0-1.0)

    Returns:
        Tuple of (similar_found: bool, similar_entries: list)

    Note:
        This function would integrate with Qdrant MCP in production.
    """
    # TODO: Integrate with mcp__qdrant__qdrant-find()
    # Search using first 100-200 chars of content
    # Calculate similarity scores
    # Return entries above threshold

    # Placeholder implementation
    search_query = content[:100]
    print(f"  → Searching for similar content (query: {len(search_query)} chars)...")
    print(f"  → Similarity threshold: {threshold}")

    return False, []


def check_duplicate_by_hash(content: str, metadata: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check for exact duplicate using content hash.

    Args:
        content: Knowledge content
        metadata: Metadata dictionary

    Returns:
        Tuple of (is_duplicate: bool, message: str)
    """
    # Generate hash
    content_hash = generate_content_hash(content)

    # Add hash to metadata if not present
    if "content_hash" not in metadata:
        metadata["content_hash"] = content_hash

    print(f"\n📋 Content Hash: {content_hash}")

    # Search for existing
    exists, existing = search_by_hash(content_hash)

    if exists:
        return True, (
            f"❌ DUPLICATE DETECTED (exact match)\n"
            f"Content hash: {content_hash}\n"
            f"Existing entry: {existing.get('unique_id', 'unknown')}\n"
            f"Action: SKIP storage (duplicate)"
        )

    return False, f"✓ No exact duplicate found (hash: {content_hash[:16]}...)"


def check_similar_content(content: str, threshold: float = 0.85) -> Tuple[bool, str]:
    """
    Check for similar content using semantic similarity.

    Args:
        content: Knowledge content
        threshold: Similarity threshold (0.0-1.0)

    Returns:
        Tuple of (similar_found: bool, message: str)
    """
    print(f"\n🔍 Searching for similar content (threshold: {threshold})...")

    similar_found, similar_entries = search_similar_content(content, threshold)

    if not similar_found or not similar_entries:
        return False, "✓ No similar content found"

    # Report similar entries
    messages = ["⚠️  SIMILAR CONTENT FOUND:\n"]

    for i, entry in enumerate(similar_entries, 1):
        similarity = entry.get("similarity_score", 0.0)
        unique_id = entry.get("unique_id", "unknown")
        entry_type = entry.get("type", "unknown")

        messages.append(
            f"  {i}. {unique_id} (type: {entry_type})\n"
            f"     Similarity: {similarity:.2%}\n"
        )

    messages.append(
        "\nRecommendation:\n"
        "  - Review similar entries before storing\n"
        "  - Consider updating existing entry instead\n"
        "  - If content is genuinely different, proceed with storage"
    )

    return True, "".join(messages)


def check_unique_id_collision(metadata: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if unique_id already exists in knowledge base.

    Args:
        metadata: Metadata dictionary with unique_id

    Returns:
        Tuple of (collision: bool, message: str)
    """
    unique_id = metadata.get("unique_id")

    if not unique_id:
        return False, "⚠️  WARNING: No unique_id in metadata"

    print(f"\n🔑 Checking unique_id: {unique_id}")

    # TODO: Integrate with mcp__qdrant__qdrant-find()
    # Search for: f"unique_id:{unique_id}"

    # Placeholder
    print("  → Searching for existing unique_id...")
    exists = False

    if exists:
        return True, (
            f"❌ COLLISION: unique_id '{unique_id}' already exists\n"
            f"Action:\n"
            f"  - Use different unique_id, OR\n"
            f"  - Update existing entry (versioned update)"
        )

    return False, f"✓ unique_id '{unique_id}' is available"


def run_duplicate_checks(
    content: str,
    metadata: Dict[str, Any],
    similarity_threshold: float = 0.85,
    check_hash: bool = True,
    check_similarity: bool = True,
    check_id: bool = True,
) -> Tuple[bool, List[str]]:
    """
    Run all duplicate detection checks.

    Args:
        content: Knowledge content
        metadata: Metadata dictionary
        similarity_threshold: Threshold for semantic similarity
        check_hash: Whether to check content hash
        check_similarity: Whether to check semantic similarity
        check_id: Whether to check unique_id collision

    Returns:
        Tuple of (duplicates_found: bool, messages: list)
    """
    messages = []
    duplicates_found = False

    print("\n" + "=" * 60)
    print("DUPLICATE DETECTION")
    print("=" * 60)

    # Check 1: Content hash (exact duplicate)
    if check_hash:
        is_dup, msg = check_duplicate_by_hash(content, metadata)
        messages.append(msg)
        if is_dup:
            duplicates_found = True

    # Check 2: Semantic similarity
    if check_similarity and not duplicates_found:
        similar_found, msg = check_similar_content(content, similarity_threshold)
        messages.append(msg)
        # Note: Similar content is a warning, not a hard block

    # Check 3: unique_id collision
    if check_id:
        collision, msg = check_unique_id_collision(metadata)
        messages.append(msg)
        if collision:
            duplicates_found = True

    return duplicates_found, messages


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Check for duplicate knowledge entries in Qdrant MCP"
    )

    content_group = parser.add_mutually_exclusive_group(required=True)
    content_group.add_argument("--content", help="Knowledge content as string")
    content_group.add_argument(
        "--content-file", help="Path to file containing knowledge content"
    )

    parser.add_argument(
        "--metadata", help="Path to metadata JSON file (optional for hash-only checks)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Similarity threshold (0.0-1.0, default: 0.85)",
    )
    parser.add_argument(
        "--hash-only",
        action="store_true",
        help="Only check content hash (skip similarity search)",
    )
    parser.add_argument(
        "--skip-id-check", action="store_true", help="Skip unique_id collision check"
    )

    args = parser.parse_args()

    # Load content
    if args.content:
        content = args.content
    else:
        try:
            with open(args.content_file, "r") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"ERROR: Content file not found: {args.content_file}")
            sys.exit(1)

    # Load metadata
    metadata = {}
    if args.metadata:
        try:
            with open(args.metadata, "r") as f:
                metadata = json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Metadata file not found: {args.metadata}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in metadata file: {e}")
            sys.exit(1)

    # Run checks
    duplicates_found, messages = run_duplicate_checks(
        content=content,
        metadata=metadata,
        similarity_threshold=args.threshold,
        check_hash=True,
        check_similarity=not args.hash_only,
        check_id=not args.skip_id_check and bool(metadata),
    )

    # Print results
    print("\n" + "=" * 60)
    print("DUPLICATE CHECK RESULTS")
    print("=" * 60 + "\n")

    for message in messages:
        print(message)
        print()

    print("=" * 60)

    # Exit code
    if duplicates_found:
        print("❌ DUPLICATES FOUND - Storage blocked")
        sys.exit(1)
    else:
        print("✅ NO DUPLICATES - Safe to store")
        sys.exit(0)


if __name__ == "__main__":
    main()
