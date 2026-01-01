#!/usr/bin/env python3
"""
Pre-Storage Validator for Qdrant MCP Knowledge Management

Validates entries BEFORE storage to prevent issues:
1. Check for duplicate unique_id across ALL collections
2. Validate required metadata fields
3. Validate content quality
4. Provide clear pass/fail with actionable messages

Usage:
    # As module
    from pre_storage_validator import validate_before_storage
    is_valid, message = validate_before_storage(information, metadata)

    # As CLI
    python pre_storage_validator.py --content "content" --metadata '{"unique_id": "test"}'

Created: 2025-12-31
"""

import os
import sys
import json
import hashlib
import argparse


# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTIONS_TO_CHECK = [
    "legal-ai-knowledge",
    "project-tracking",
    "legal-ai-best-practices",
]

REQUIRED_FIELDS = ["unique_id", "type", "component", "importance", "created_at"]
VALID_TYPES = [
    "architecture_decision",
    "agent_spec",
    "story_outcome",
    "error_pattern",
    "database_schema",
    "config_pattern",
    "integration_example",
    "best_practice",
]
VALID_IMPORTANCE = ["critical", "high", "medium", "low"]

# Content quality thresholds
MIN_CONTENT_LENGTH = 100
MAX_CONTENT_LENGTH = 50000


def get_qdrant_client():
    """Get Qdrant client with API key from environment."""
    try:
        from qdrant_client import QdrantClient
    except ImportError:
        return None, "qdrant-client not installed"

    api_key = os.getenv("QDRANT_KNOWLEDGE_BASE_API_KEY")
    if not api_key:
        return None, "QDRANT_KNOWLEDGE_BASE_API_KEY not set"

    try:
        client = QdrantClient(url=QDRANT_URL, api_key=api_key)
        return client, None
    except Exception as e:
        return None, f"Connection failed: {e}"


def check_duplicate_unique_id(client, unique_id: str) -> tuple[bool, str]:
    """
    Check if unique_id already exists in any collection.

    Returns:
        (is_duplicate, message)
    """
    if not unique_id:
        return False, "No unique_id to check"

    for coll_name in COLLECTIONS_TO_CHECK:
        try:
            scroll_result = client.scroll(
                collection_name=coll_name,
                limit=500,
                with_payload=True,
                with_vectors=False,
            )

            for point in scroll_result[0]:
                payload = point.payload or {}
                existing_id = (
                    payload.get("unique_id")
                    or (payload.get("metadata") or {}).get("unique_id")
                    or ""
                )
                if existing_id == unique_id:
                    return True, (
                        f"DUPLICATE: '{unique_id}' already exists in '{coll_name}' "
                        f"(point_id: {point.id})"
                    )

        except Exception as e:
            # Collection might not exist yet - that's OK
            if "not found" not in str(e).lower():
                print(f"Warning: Could not check {coll_name}: {e}")

    return False, f"'{unique_id}' is available"


def check_similar_content(
    client, content: str, threshold: float = 0.9
) -> tuple[bool, list]:
    """
    Check for highly similar content using content hash.

    For now, uses exact hash matching. Future: semantic similarity.

    Returns:
        (similar_found, similar_entries)
    """
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    similar = []

    for coll_name in COLLECTIONS_TO_CHECK:
        try:
            scroll_result = client.scroll(
                collection_name=coll_name,
                limit=500,
                with_payload=True,
                with_vectors=False,
            )

            for point in scroll_result[0]:
                payload = point.payload or {}
                existing_hash = (
                    payload.get("content_hash")
                    or (payload.get("metadata") or {}).get("content_hash")
                    or ""
                )
                if existing_hash == content_hash:
                    uid = (
                        payload.get("unique_id")
                        or (payload.get("metadata") or {}).get("unique_id")
                        or ""
                    )
                    similar.append(
                        {
                            "collection": coll_name,
                            "unique_id": uid,
                            "match_type": "exact_hash",
                        }
                    )

        except Exception:
            pass  # Skip unavailable collections

    return len(similar) > 0, similar


def validate_metadata_fields(metadata: dict) -> tuple[bool, list]:
    """
    Validate required metadata fields and values.

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    missing = [f for f in REQUIRED_FIELDS if f not in metadata]
    if missing:
        errors.append(f"Missing required fields: {missing}")

    # Validate type
    entry_type = metadata.get("type", "")
    if entry_type and entry_type not in VALID_TYPES:
        errors.append(f"Invalid type '{entry_type}'. Must be one of: {VALID_TYPES}")

    # Validate importance
    importance = metadata.get("importance", "")
    if importance and importance not in VALID_IMPORTANCE:
        errors.append(f"Invalid importance '{importance}'. Must be: {VALID_IMPORTANCE}")

    # Validate unique_id format (basic check)
    unique_id = metadata.get("unique_id", "")
    if unique_id and len(unique_id) < 5:
        errors.append(f"unique_id '{unique_id}' too short (min 5 characters)")

    # Validate created_at format
    created_at = metadata.get("created_at", "")
    if created_at:
        # Accept YYYY-MM-DD or ISO 8601
        import re

        if not re.match(r"^\d{4}-\d{2}-\d{2}", created_at):
            errors.append(f"created_at '{created_at}' must be YYYY-MM-DD format")

    return len(errors) == 0, errors


def validate_content_quality(content: str) -> tuple[bool, list]:
    """
    Validate content meets quality thresholds.

    Returns:
        (is_valid, warnings_or_errors)
    """
    messages = []

    if len(content) < MIN_CONTENT_LENGTH:
        messages.append(
            f"Content too short ({len(content)} chars). "
            f"Minimum {MIN_CONTENT_LENGTH} chars for meaningful knowledge."
        )

    if len(content) > MAX_CONTENT_LENGTH:
        messages.append(
            f"Content too long ({len(content)} chars). "
            f"Maximum {MAX_CONTENT_LENGTH} chars. Consider splitting into multiple entries."
        )

    # Check for placeholder text
    placeholders = ["TODO", "FIXME", "TBD", "[INSERT", "[PLACEHOLDER"]
    for p in placeholders:
        if p in content.upper():
            messages.append(f"Content contains placeholder text: '{p}'")

    return len(messages) == 0, messages


def validate_before_storage(
    information: str,
    metadata: dict,
    skip_duplicate_check: bool = False,
    skip_similarity_check: bool = False,
) -> tuple[bool, str, dict]:
    """
    Complete pre-storage validation.

    Args:
        information: The knowledge content to store
        metadata: Metadata dictionary
        skip_duplicate_check: Skip Qdrant duplicate check (for offline validation)
        skip_similarity_check: Skip content similarity check

    Returns:
        (is_valid, message, details)

    Details dict contains:
        - errors: list of error messages (blocking)
        - warnings: list of warning messages (non-blocking)
        - content_hash: SHA256 hash of content
        - checks_performed: list of checks that ran
    """
    details = {
        "errors": [],
        "warnings": [],
        "content_hash": hashlib.sha256(information.encode("utf-8")).hexdigest(),
        "checks_performed": [],
    }

    # 1. Validate metadata fields
    details["checks_performed"].append("metadata_fields")
    is_valid, errors = validate_metadata_fields(metadata)
    if not is_valid:
        details["errors"].extend(errors)

    # 2. Validate content quality
    details["checks_performed"].append("content_quality")
    is_valid, messages = validate_content_quality(information)
    if not is_valid:
        # Content issues are warnings, not blocking errors
        details["warnings"].extend(messages)

    # 3. Check for duplicate unique_id (requires Qdrant connection)
    if not skip_duplicate_check:
        client, error = get_qdrant_client()
        if client:
            details["checks_performed"].append("duplicate_unique_id")
            unique_id = metadata.get("unique_id", "")
            is_dup, msg = check_duplicate_unique_id(client, unique_id)
            if is_dup:
                details["errors"].append(msg)

            # 4. Check for similar content
            if not skip_similarity_check:
                details["checks_performed"].append("similar_content")
                similar_found, similar_entries = check_similar_content(
                    client, information
                )
                if similar_found:
                    for entry in similar_entries:
                        details["warnings"].append(
                            f"Similar content found: {entry['unique_id']} in {entry['collection']}"
                        )
        else:
            details["warnings"].append(
                f"Qdrant unavailable ({error}) - skipping duplicate check"
            )

    # Build result message
    if details["errors"]:
        message = "VALIDATION FAILED:\n" + "\n".join(
            f"  - {e}" for e in details["errors"]
        )
        if details["warnings"]:
            message += "\n\nWarnings:\n" + "\n".join(
                f"  - {w}" for w in details["warnings"]
            )
        return False, message, details

    if details["warnings"]:
        message = "VALIDATION PASSED with warnings:\n" + "\n".join(
            f"  - {w}" for w in details["warnings"]
        )
        return True, message, details

    return True, "VALIDATION PASSED", details


def main():
    parser = argparse.ArgumentParser(
        description="Pre-storage validation for Qdrant MCP knowledge entries"
    )

    parser.add_argument("--content", help="Knowledge content as string")
    parser.add_argument("--content-file", help="File containing knowledge content")
    parser.add_argument("--metadata", help="Metadata as JSON string")
    parser.add_argument("--metadata-file", help="File containing metadata JSON")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip Qdrant checks (offline validation only)",
    )

    args = parser.parse_args()

    # Load content
    if args.content:
        content = args.content
    elif args.content_file:
        with open(args.content_file, "r") as f:
            content = f.read()
    else:
        print("ERROR: Must provide --content or --content-file")
        sys.exit(1)

    # Load metadata
    if args.metadata:
        metadata = json.loads(args.metadata)
    elif args.metadata_file:
        with open(args.metadata_file, "r") as f:
            metadata = json.load(f)
    else:
        print("ERROR: Must provide --metadata or --metadata-file")
        sys.exit(1)

    # Run validation
    is_valid, message, details = validate_before_storage(
        content, metadata, skip_duplicate_check=args.offline
    )

    print("\n" + "=" * 60)
    print("PRE-STORAGE VALIDATION")
    print("=" * 60)
    print(f"\nContent hash: {details['content_hash'][:16]}...")
    print(f"Checks performed: {', '.join(details['checks_performed'])}")
    print("\n" + message)
    print("\n" + "=" * 60)

    if is_valid:
        print("RESULT: SAFE TO STORE")
        sys.exit(0)
    else:
        print("RESULT: DO NOT STORE")
        sys.exit(1)


if __name__ == "__main__":
    main()
