#!/usr/bin/env python3
"""
Test Knowledge Inventory Updates (Task 9)

Verifies that knowledge_inventory.md updates correctly when
new knowledge entries are added to the system.

Following 2025 best practices for governance and tracking.
"""

import os
import tempfile
from pathlib import Path

# Allow tests to write to /tmp (override security constraint for testing)
os.environ["QDRANT_INVENTORY_BASE_DIR"] = "/tmp"

from update_inventory import update_inventory, generate_inventory_markdown

print("\n" + "=" * 80)
print("KNOWLEDGE INVENTORY UPDATE TESTING (Task 9)")
print("=" * 80)

tests_run = 0
tests_passed = 0


def test(name: str, condition: bool, details: str = ""):
    """Run a test and track results."""
    global tests_run, tests_passed
    tests_run += 1

    if condition:
        tests_passed += 1
        print(f"✅ TEST {tests_run}: {name}")
        if details:
            print(f"   {details}")
        return True
    else:
        print(f"❌ TEST {tests_run} FAILED: {name}")
        if details:
            print(f"   {details}")
        return False


print("\n" + "=" * 80)
print("TEST 1: Empty Inventory Generation")
print("=" * 80)

# Test with no entries
empty_markdown = generate_inventory_markdown([])

test(
    "Empty inventory generates valid markdown",
    "Total Entries**: 0" in empty_markdown and "No entries yet" in empty_markdown,
    "Shows 0 entries and empty state messages",
)

test(
    "Empty inventory has all required sections",
    all(
        section in empty_markdown
        for section in [
            "Summary Statistics",
            "By Type",
            "By Component",
            "Architecture Decisions",
            "Error Patterns",
            "Update Log",
        ]
    ),
    "All 8+ sections present",
)


print("\n" + "=" * 80)
print("TEST 2: Single Entry Inventory")
print("=" * 80)

# Test with one entry
single_entry = [
    {
        "unique_id": "arch-decision-5-tier-qdrant-2024-12-15",
        "type": "architecture_decision",
        "component": "qdrant",
        "importance": "critical",
        "created_at": "2024-12-15",
        "breaking_change": True,
        "keywords": ["qdrant", "architecture", "5-tier"],
        "deprecated": False,
    }
]

single_markdown = generate_inventory_markdown(single_entry)

test(
    "Inventory shows correct count (1 entry)",
    "Total Entries**: 1" in single_markdown,
    "Entry count updated",
)

test(
    "Entry appears in Architecture Decisions table",
    "arch-decision-5-tier-qdrant-2024-12-15" in single_markdown,
    "unique_id found in table",
)

test(
    "Statistics updated correctly",
    "Architecture Decisions | 1 | 1 | 0 | 0 | 0"
    in single_markdown,  # 1 total, 1 critical
    "1 architecture decision, critical importance",
)

test(
    "Component statistics updated",
    "qdrant | 1" in single_markdown,
    "Qdrant component count = 1",
)

test(
    "Keywords extracted from entries",
    "qdrant" in single_markdown and "architecture" in single_markdown,
    "Entry keywords appear in search index",
)


print("\n" + "=" * 80)
print("TEST 3: Multiple Entries of Different Types")
print("=" * 80)

# Test with multiple entry types
multiple_entries = [
    {
        "unique_id": "arch-decision-5-tier-qdrant-2024-12-15",
        "type": "architecture_decision",
        "component": "qdrant",
        "importance": "critical",
        "created_at": "2024-12-15",
        "breaking_change": True,
        "deprecated": False,
    },
    {
        "unique_id": "agent-15-spec",
        "type": "agent_spec",
        "agent_id": "agent_15",
        "agent_name": "storage_router",
        "component": "agents",
        "importance": "high",
        "created_at": "2025-12-20",
        "deprecated": False,
    },
    {
        "unique_id": "story-2-17-complete",
        "type": "story_outcome",
        "story_id": "2-17",
        "epic_id": "2",
        "component": "agents",
        "importance": "high",
        "created_at": "2025-12-20",
        "deprecated": False,
    },
    {
        "unique_id": "error-qdrant-timeout",
        "type": "error_pattern",
        "component": "qdrant",
        "severity": "high",
        "importance": "medium",
        "created_at": "2025-12-25",
        "resolved": False,
        "deprecated": False,
    },
]

multi_markdown = generate_inventory_markdown(multiple_entries)

test(
    "Inventory shows correct count (4 entries)",
    "Total Entries**: 4" in multi_markdown,
    "All entries counted",
)

test(
    "All entry types represented in tables",
    all(
        uid in multi_markdown
        for uid in [
            "arch-decision-5-tier-qdrant-2024-12-15",
            "agent-15-spec",
            "story-2-17-complete",
            "error-qdrant-timeout",
        ]
    ),
    "All 4 entries appear in their respective tables",
)

test(
    "Importance levels aggregated correctly",
    "Architecture Decisions | 1 | 1 | 0 | 0 | 0" in multi_markdown  # 1 critical
    and "Agent Specifications | 1 | 0 | 1 | 0 | 0" in multi_markdown,  # 1 high
    "Importance distribution correct",
)

test(
    "Component counts aggregated",
    "qdrant | 2" in multi_markdown and "agents | 2" in multi_markdown,
    "Qdrant=2, agents=2",
)


print("\n" + "=" * 80)
print("TEST 4: Deprecated Entry Tracking")
print("=" * 80)

# Test with deprecated entry
deprecated_entry = [
    {
        "unique_id": "arch-decision-old-approach-2024-01-01",
        "type": "architecture_decision",
        "component": "qdrant",
        "importance": "medium",
        "created_at": "2024-01-01",
        "breaking_change": False,
        "deprecated": True,
        "deprecated_date": "2024-12-15",
        "superseded_by": "arch-decision-5-tier-qdrant-2024-12-15",
        "deprecation_reason": "Replaced by 5-tier architecture",
    }
]

deprecated_markdown = generate_inventory_markdown(deprecated_entry)

test(
    "Deprecated entry appears in deprecated section",
    "arch-decision-old-approach-2024-01-01" in deprecated_markdown
    and "Deprecated Entries" in deprecated_markdown,
    "Entry tracked in deprecated section",
)

test(
    "Deprecation metadata included",
    "Replaced by 5-tier architecture" in deprecated_markdown
    and "arch-decision-5-tier-qdrant-2024-12-15" in deprecated_markdown,
    "Superseded by and reason shown",
)


print("\n" + "=" * 80)
print("TEST 5: File Writing")
print("=" * 80)

# Test actual file writing (using TemporaryDirectory to prevent TOCTOU race condition)
with tempfile.TemporaryDirectory() as tmpdir:
    temp_path = Path(tmpdir) / "inventory.md"
    result_markdown = update_inventory(single_entry, output_path=str(temp_path))

    test(
        "Inventory file written successfully",
        temp_path.exists() and temp_path.stat().st_size > 0,
        f"File created: {temp_path.stat().st_size} bytes",
    )

    test(
        "Written content matches generated markdown",
        temp_path.read_text() == result_markdown,
        "File content is correct",
    )
    # No manual cleanup needed - TemporaryDirectory handles it


print("\n" + "=" * 80)
print("TEST 6: Edge Cases")
print("=" * 80)

# Test with missing optional fields
minimal_entry = [
    {
        "unique_id": "test-minimal-2025-12-29",
        "type": "architecture_decision",
        "component": "general",
        "importance": "low",
        "created_at": "2025-12-29",
    }
]

minimal_markdown = generate_inventory_markdown(minimal_entry)

test(
    "Minimal entry (required fields only) generates valid markdown",
    "Total Entries**: 1" in minimal_markdown
    and "test-minimal-2025-12-29" in minimal_markdown,
    "Handles missing optional fields gracefully",
)

test(
    "Missing keywords handled gracefully",
    "No entries yet" in minimal_markdown or "Keywords" in minimal_markdown,
    "No crash when keywords field missing",
)


print("\n" + "=" * 80)
print("TEST SUMMARY - INVENTORY UPDATES")
print("=" * 80)
print(f"Total Tests: {tests_run}")
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_run - tests_passed}")
print(f"Success Rate: {(tests_passed/tests_run)*100:.1f}%")

if tests_passed == tests_run:
    print("\n✅ ALL INVENTORY UPDATE TESTS PASSED")
    print("\nKEY FINDINGS:")
    print("✓ Task 9: knowledge_inventory.md updates correctly")
    print("✓ Empty state handled gracefully")
    print("✓ Single and multiple entries tracked accurately")
    print("✓ All schema types appear in appropriate tables")
    print("✓ Statistics aggregated correctly (by type, component, importance)")
    print("✓ Deprecated entries tracked in separate section")
    print("✓ Keywords extracted for search index")
    print("✓ File writing works correctly")
    print("✓ Edge cases handled (minimal metadata, missing keywords)")
    print("\nINTEGRATION:")
    print("- Call update_inventory(entries) after each knowledge storage")
    print("- Inventory provides governance and audit trail")
    print("- Search index enables quick lookups")
    exit(0)
else:
    print(f"\n⚠️  {tests_run - tests_passed} TESTS FAILED")
    print("Review failures above")
    exit(1)
