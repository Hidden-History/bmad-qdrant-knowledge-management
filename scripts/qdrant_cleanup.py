#!/usr/bin/env python3
"""
Qdrant Knowledge Base Cleanup Script

Safely identifies and removes duplicate, invalid, or test entries from Qdrant collections.
Includes pre-deletion verification, backup recommendations, and post-cleanup validation.

Configuration is loaded from config.py.

Usage:
    python qdrant_cleanup.py --audit                    # Audit only (safe, no changes)
    python qdrant_cleanup.py --delete --dry-run         # Show what would be deleted
    python qdrant_cleanup.py --delete --execute         # Execute deletion (prompts for confirmation)
    python qdrant_cleanup.py --delete --test-only       # Only delete test-* entries
    python qdrant_cleanup.py --validate-entry UNIQUE_ID # Validate single entry exists
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    KNOWLEDGE_COLLECTION,
    BEST_PRACTICES_COLLECTION,
)


def get_client():
    """Get Qdrant client with API key from environment."""
    try:
        from qdrant_client import QdrantClient
    except ImportError:
        print("ERROR: qdrant-client not installed. Run: pip install qdrant-client")
        sys.exit(1)

    if QDRANT_API_KEY:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    else:
        return QdrantClient(url=QDRANT_URL)


def get_unique_id(payload: dict) -> str:
    """Extract unique_id from payload (handles MCP and population script formats)."""
    if not payload:
        return ""
    return (
        payload.get("unique_id")
        or (payload.get("metadata") or {}).get("unique_id")
        or ""
    )


def audit_collection(client, collection_name: str) -> dict:
    """
    Audit a single collection for issues.

    Returns dict with:
    - total_entries: int
    - duplicates: list of {point_id, unique_id, first_seen_at}
    - invalid: list of {point_id, unique_id, missing_fields}
    - test_entries: list of {point_id, unique_id}
    """
    issues = {
        "collection": collection_name,
        "total_entries": 0,
        "duplicates": [],
        "invalid": [],
        "test_entries": [],
    }

    seen_ids = {}
    required_fields = ["unique_id", "type", "component", "importance"]

    try:
        scroll_result = client.scroll(
            collection_name=collection_name,
            limit=500,
            with_payload=True,
            with_vectors=False,
        )
    except Exception as e:
        print(f"  ERROR reading {collection_name}: {e}")
        return issues

    points = scroll_result[0]
    issues["total_entries"] = len(points)

    for point in points:
        payload = point.payload or {}
        unique_id = get_unique_id(payload)

        # Check for duplicates
        if unique_id:
            if unique_id in seen_ids:
                issues["duplicates"].append(
                    {
                        "point_id": str(point.id),
                        "unique_id": unique_id,
                        "first_seen_at": str(seen_ids[unique_id]),
                    }
                )
            else:
                seen_ids[unique_id] = point.id

            # Check for test entries
            if "test-" in str(unique_id).lower() or "e2e-" in str(unique_id).lower():
                issues["test_entries"].append(
                    {"point_id": str(point.id), "unique_id": unique_id}
                )

        # Check for invalid entries (missing required fields)
        metadata = payload.get("metadata") or payload
        missing = []
        for field in required_fields:
            if field not in metadata and field not in payload:
                missing.append(field)

        if missing:
            issues["invalid"].append(
                {
                    "point_id": str(point.id),
                    "unique_id": unique_id or "(no unique_id)",
                    "missing_fields": missing,
                }
            )

    return issues


def print_audit_results(all_issues: list):
    """Print formatted audit results."""
    print("\n" + "=" * 70)
    print("QDRANT KNOWLEDGE BASE AUDIT RESULTS")
    print("=" * 70)

    total_entries = 0
    total_duplicates = 0
    total_invalid = 0
    total_test = 0

    for issues in all_issues:
        coll = issues["collection"]
        total_entries += issues["total_entries"]

        print(f"\n## Collection: {coll}")
        print(f"   Total entries: {issues['total_entries']}")

        if issues["duplicates"]:
            print(f"\n   DUPLICATES ({len(issues['duplicates'])}):")
            for item in issues["duplicates"]:
                print(f"     - {item['unique_id']}")
                print(
                    f"       point_id: {item['point_id']}, first_seen: {item['first_seen_at']}"
                )
            total_duplicates += len(issues["duplicates"])

        if issues["invalid"]:
            print(f"\n   INVALID ENTRIES ({len(issues['invalid'])}):")
            for item in issues["invalid"]:
                print(f"     - {item['unique_id']}")
                print(f"       missing: {item['missing_fields']}")
            total_invalid += len(issues["invalid"])

        if issues["test_entries"]:
            print(f"\n   TEST ENTRIES ({len(issues['test_entries'])}):")
            for item in issues["test_entries"]:
                print(f"     - {item['unique_id']} (point: {item['point_id']})")
            total_test += len(issues["test_entries"])

        if (
            not issues["duplicates"]
            and not issues["invalid"]
            and not issues["test_entries"]
        ):
            print("   No issues found")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total entries across all collections: {total_entries}")
    print(f"Duplicates found: {total_duplicates}")
    print(f"Invalid entries found: {total_invalid}")
    print(f"Test entries found: {total_test}")
    print(f"Total issues: {total_duplicates + total_invalid + total_test}")
    print("=" * 70)


def collect_deletion_candidates(
    all_issues: list,
    test_only: bool = False,
    duplicates_only: bool = False,
    invalid_only: bool = False,
) -> dict:
    """Collect entries to delete based on options."""
    candidates = {}  # collection_name -> list of point_ids

    for issues in all_issues:
        coll = issues["collection"]
        candidates[coll] = []

        if not test_only and not invalid_only:
            # Duplicates (always safe to delete - keep first occurrence)
            for item in issues["duplicates"]:
                candidates[coll].append(
                    {
                        "point_id": item["point_id"],
                        "unique_id": item["unique_id"],
                        "reason": "duplicate",
                    }
                )

        if not duplicates_only and not test_only:
            # Invalid entries
            for item in issues["invalid"]:
                # Don't delete if also a duplicate (already in list)
                if item["point_id"] not in [c["point_id"] for c in candidates[coll]]:
                    candidates[coll].append(
                        {
                            "point_id": item["point_id"],
                            "unique_id": item["unique_id"],
                            "reason": f"invalid (missing: {item['missing_fields']})",
                        }
                    )

        if not duplicates_only and not invalid_only:
            # Test entries
            for item in issues["test_entries"]:
                if item["point_id"] not in [c["point_id"] for c in candidates[coll]]:
                    candidates[coll].append(
                        {
                            "point_id": item["point_id"],
                            "unique_id": item["unique_id"],
                            "reason": "test entry",
                        }
                    )

    return candidates


def print_deletion_plan(candidates: dict) -> int:
    """Print what will be deleted and return total count."""
    print("\n" + "=" * 70)
    print("DELETION PLAN")
    print("=" * 70)

    total = 0
    for coll, entries in candidates.items():
        if entries:
            print(f"\n## {coll} ({len(entries)} entries)")
            for entry in entries:
                print(f"   - {entry['unique_id']}")
                print(f"     reason: {entry['reason']}")
                total += 1

    print("\n" + "=" * 70)
    print(f"TOTAL TO DELETE: {total} entries")
    print("=" * 70)

    return total


def execute_deletion(client, candidates: dict, dry_run: bool = True) -> dict:
    """Execute deletion of candidates."""
    results = {"dry_run": dry_run, "collections": {}, "total_deleted": 0, "errors": []}

    for coll, entries in candidates.items():
        if not entries:
            continue

        point_ids = [entry["point_id"] for entry in entries]

        if dry_run:
            print(f"[DRY RUN] Would delete {len(entries)} entries from {coll}")
            results["collections"][coll] = {
                "would_delete": len(entries),
                "point_ids": point_ids,
            }
        else:
            try:
                client.delete(collection_name=coll, points_selector=point_ids)
                print(f"Deleted {len(entries)} entries from {coll}")
                results["collections"][coll] = {
                    "deleted": len(entries),
                    "point_ids": point_ids,
                }
                results["total_deleted"] += len(entries)
            except Exception as e:
                error_msg = f"Error deleting from {coll}: {e}"
                print(f"ERROR: {error_msg}")
                results["errors"].append(error_msg)

    return results


def verify_deletion(client, candidates: dict) -> bool:
    """Verify entries were deleted."""
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    all_verified = True

    for coll, entries in candidates.items():
        if not entries:
            continue

        unique_ids = [entry["unique_id"] for entry in entries]

        try:
            scroll_result = client.scroll(
                collection_name=coll, limit=500, with_payload=True, with_vectors=False
            )

            still_present = []
            for point in scroll_result[0]:
                uid = get_unique_id(point.payload or {})
                if uid in unique_ids:
                    still_present.append(uid)

            if still_present:
                print(f"\n{coll}: FAILED - {len(still_present)} entries still present:")
                for uid in still_present:
                    print(f"  - {uid}")
                all_verified = False
            else:
                print(f"\n{coll}: VERIFIED - All {len(entries)} entries removed")

        except Exception as e:
            print(f"\n{coll}: ERROR verifying - {e}")
            all_verified = False

    return all_verified


def export_backup(client, collection_name: str, output_dir: str = "."):
    """Export collection to JSON backup file."""
    try:
        scroll_result = client.scroll(
            collection_name=collection_name,
            limit=1000,
            with_payload=True,
            with_vectors=True,
        )

        entries = []
        for point in scroll_result[0]:
            entries.append(
                {
                    "id": str(point.id),
                    "payload": point.payload,
                    "vector": list(point.vector) if point.vector else None,
                }
            )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{output_dir}/backup_{collection_name}_{timestamp}.json"

        with open(backup_file, "w") as f:
            json.dump(entries, f, indent=2)

        print(f"Backup saved: {backup_file} ({len(entries)} entries)")
        return backup_file

    except Exception as e:
        print(f"ERROR creating backup: {e}")
        return None


def validate_single_entry(client, unique_id: str):
    """Check if a specific entry exists and show its details."""
    print(f"\nSearching for: {unique_id}")
    print("=" * 70)

    found = False

    # Use configured collection names
    for coll_name in [KNOWLEDGE_COLLECTION, BEST_PRACTICES_COLLECTION]:
        try:
            scroll_result = client.scroll(
                collection_name=coll_name,
                limit=500,
                with_payload=True,
                with_vectors=False,
            )

            for point in scroll_result[0]:
                uid = get_unique_id(point.payload or {})
                if uid == unique_id:
                    print(f"\nFOUND in {coll_name}:")
                    print(f"  Point ID: {point.id}")
                    print(f"  Payload: {json.dumps(point.payload, indent=4)}")
                    found = True

        except Exception as e:
            print(f"Error searching {coll_name}: {e}")

    if not found:
        print(f"\nNOT FOUND: '{unique_id}' does not exist in any collection")


def main():
    parser = argparse.ArgumentParser(description="Qdrant Knowledge Base Cleanup Script")

    # Main actions
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--audit",
        action="store_true",
        help="Audit collections for issues (safe, no changes)",
    )
    action_group.add_argument(
        "--delete", action="store_true", help="Delete problematic entries"
    )
    action_group.add_argument(
        "--backup", metavar="COLLECTION", help="Export collection to JSON backup"
    )
    action_group.add_argument(
        "--validate-entry", metavar="UNIQUE_ID", help="Check if specific entry exists"
    )

    # Deletion options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Actually execute the deletion"
    )
    parser.add_argument(
        "--test-only", action="store_true", help="Only delete test-* entries"
    )
    parser.add_argument(
        "--duplicates-only", action="store_true", help="Only delete duplicate entries"
    )
    parser.add_argument(
        "--invalid-only", action="store_true", help="Only delete invalid entries"
    )
    parser.add_argument(
        "--no-verify", action="store_true", help="Skip post-deletion verification"
    )

    # Output options
    parser.add_argument("--output-dir", default=".", help="Directory for backup files")

    args = parser.parse_args()

    # Get client
    client = get_client()

    # List collections
    collections = client.get_collections()
    collection_names = [c.name for c in collections.collections]
    print(f"\nFound {len(collection_names)} collections: {', '.join(collection_names)}")

    # Execute action
    if args.audit:
        all_issues = []
        for coll in collection_names:
            print(f"\nAuditing {coll}...")
            issues = audit_collection(client, coll)
            all_issues.append(issues)

        print_audit_results(all_issues)

    elif args.delete:
        if not args.dry_run and not args.execute:
            print("ERROR: Must specify --dry-run or --execute")
            sys.exit(1)

        # Audit first
        all_issues = []
        for coll in collection_names:
            print(f"Auditing {coll}...")
            issues = audit_collection(client, coll)
            all_issues.append(issues)

        # Collect candidates
        candidates = collect_deletion_candidates(
            all_issues,
            test_only=args.test_only,
            duplicates_only=args.duplicates_only,
            invalid_only=args.invalid_only,
        )

        # Show plan
        total = print_deletion_plan(candidates)

        if total == 0:
            print("\nNo entries to delete.")
            sys.exit(0)

        # Execute or dry-run
        if args.execute:
            print("\n" + "!" * 70)
            print("WARNING: This will permanently delete the entries listed above!")
            print("!" * 70)
            confirm = input("\nType 'DELETE' to confirm: ")

            if confirm != "DELETE":
                print("Aborted.")
                sys.exit(0)

            results = execute_deletion(client, candidates, dry_run=False)

            if not args.no_verify:
                verify_deletion(client, candidates)

            print(f"\nCompleted. Deleted {results['total_deleted']} entries.")

        else:
            execute_deletion(client, candidates, dry_run=True)
            print("\n[DRY RUN] No changes made. Use --execute to delete.")

    elif args.backup:
        export_backup(client, args.backup, args.output_dir)

    elif args.validate_entry:
        validate_single_entry(client, args.validate_entry)


if __name__ == "__main__":
    main()
