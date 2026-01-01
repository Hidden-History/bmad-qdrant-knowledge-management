#!/usr/bin/env python3
"""
Comprehensive Validation Testing Script

Tests the validation system with:
1. Valid metadata from actual population scripts
2. Deliberately broken metadata to test error detection
3. All 8 schema types
4. Edge cases (missing fields, invalid values, wrong formats)
"""

from validate_metadata import run_all_validations
from check_duplicates import generate_content_hash

print("\n" + "=" * 80)
print("PHASE 5: COMPREHENSIVE VALIDATION TESTING")
print("=" * 80)

# Test Counter
tests_run = 0
tests_passed = 0


def test_case(name: str, metadata: dict, should_pass: bool):
    """Run a test case and report results."""
    global tests_run, tests_passed
    tests_run += 1

    print(f"\n{'─'*80}")
    print(f"TEST {tests_run}: {name}")
    print(f"Expected: {'✓ PASS' if should_pass else '✗ FAIL'}")

    all_valid, messages = run_all_validations(metadata)

    # Print first 2 messages for context
    for msg in messages[:2]:
        print(f"  {msg}")

    success = all_valid == should_pass
    if success:
        tests_passed += 1
        print("Result: ✅ TEST PASSED")
    else:
        print(f"Result: ❌ TEST FAILED (got {'PASS' if all_valid else 'FAIL'})")

    return success


print("\n" + "=" * 80)
print("TASK 1: Test validate_metadata.py with all 8 schema types")
print("=" * 80)

# TASK 1: Valid metadata for each schema type
test_case(
    "architecture_decision (valid)",
    {
        "unique_id": "arch-decision-test-system-2025-12-29",
        "type": "architecture_decision",
        "component": "qdrant",
        "importance": "critical",
        "created_at": "2025-12-29",
        "breaking_change": True,
    },
    should_pass=True,
)

test_case(
    "agent_spec (valid)",
    {
        "unique_id": "agent-15-spec",
        "type": "agent_spec",
        "agent_id": "agent_15",
        "agent_name": "storage_router",
        "component": "agents",
        "importance": "high",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

test_case(
    "story_outcome (valid)",
    {
        "unique_id": "story-2-5-metadata-extraction-2025-12-29",
        "type": "story_outcome",
        "story_id": "2-5",
        "component": "metadata-validation",
        "importance": "medium",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

test_case(
    "error_pattern (valid)",
    {
        "unique_id": "error-qdrant-timeout-2025-12-29",
        "type": "error_pattern",
        "component": "qdrant",
        "importance": "high",
        "severity": "high",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

test_case(
    "database_schema (valid)",
    {
        "unique_id": "schema-books-2025-12-29",
        "type": "database_schema",
        "table_name": "books",
        "component": "postgres",
        "importance": "critical",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

test_case(
    "config_pattern (valid)",
    {
        "unique_id": "config-qdrant-connection-2025-12-29",
        "type": "config_pattern",
        "component": "qdrant",
        "importance": "high",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

test_case(
    "integration_example (valid)",
    {
        "unique_id": "integration-agent15-qdrant-2025-12-29",
        "type": "integration_example",
        "component": "agents",
        "importance": "medium",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

test_case(
    "best_practice (valid)",
    {
        "unique_id": "bp-qdrant-batch-upsert-2025-12-29",
        "type": "best_practice",
        "domain": "vector-storage",
        "component": "qdrant",
        "importance": "high",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

print("\n" + "=" * 80)
print("TASK 4: Test metadata validation catches invalid fields")
print("=" * 80)

test_case(
    "Missing required field (importance)",
    {
        "unique_id": "arch-decision-test-2025-12-29",
        "type": "architecture_decision",
        "component": "qdrant",
        # Missing: importance
        "created_at": "2025-12-29",
        "breaking_change": True,
    },
    should_pass=False,
)

test_case(
    "Invalid importance level",
    {
        "unique_id": "arch-decision-test-2025-12-29",
        "type": "architecture_decision",
        "component": "qdrant",
        "importance": "super-critical",  # Invalid value
        "created_at": "2025-12-29",
        "breaking_change": True,
    },
    should_pass=False,
)

test_case(
    "Wrong unique_id prefix",
    {
        "unique_id": "wrong-prefix-test-2025-12-29",  # Should start with arch-decision-
        "type": "architecture_decision",
        "component": "qdrant",
        "importance": "critical",
        "created_at": "2025-12-29",
        "breaking_change": True,
    },
    should_pass=False,  # Will generate warning but might pass
)

test_case(
    "Invalid component enum value",
    {
        "unique_id": "arch-decision-test-2025-12-29",
        "type": "architecture_decision",
        "component": "invalid_component",  # Not in enum list
        "importance": "critical",
        "created_at": "2025-12-29",
        "breaking_change": True,
    },
    should_pass=False,
)

print("\n" + "=" * 80)
print("TASK 2 & 5-7: Test check_duplicates.py")
print("=" * 80)

# Test duplicate detection
content1 = "This is a test content for duplicate detection."
content2 = "This is a test content for duplicate detection."  # Exact duplicate
content3 = "This is completely different content."

hash1 = generate_content_hash(content1)
hash2 = generate_content_hash(content2)
hash3 = generate_content_hash(content3)

print(f"\nContent 1 hash: {hash1[:16]}...")
print(
    f"Content 2 hash: {hash2[:16]}... {'✅ MATCH' if hash1 == hash2 else '❌ NO MATCH'}"
)
print(
    f"Content 3 hash: {hash3[:16]}... {'✅ DIFFERENT' if hash1 != hash3 else '❌ SAME'}"
)

if hash1 == hash2 and hash1 != hash3:
    print("✅ TEST PASSED: Exact duplicate detection works")
    tests_passed += 1
else:
    print("❌ TEST FAILED: Duplicate detection error")
tests_run += 1

# Summary
print("\n" + "=" * 80)
print("VALIDATION TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {tests_run}")
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_run - tests_passed}")
print(f"Success Rate: {(tests_passed/tests_run)*100:.1f}%")

if tests_passed == tests_run:
    print("\n✅ ALL VALIDATION TESTS PASSED")
    print("\nKEY FINDINGS:")
    print("✓ validate_metadata.py works with all 8 schema types")
    print("✓ Required field validation works correctly")
    print("✓ Importance level validation works correctly")
    print("✓ unique_id format validation works correctly")
    print("✓ Enum validation works correctly")
    print("✓ Duplicate detection works correctly")
    exit(0)
else:
    print(f"\n⚠️  {tests_run - tests_passed} TESTS NEED REVIEW")
    exit(1)
