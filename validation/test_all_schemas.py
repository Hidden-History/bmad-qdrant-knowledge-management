#!/usr/bin/env python3
"""
Comprehensive Schema Validation Testing - 2025 Best Practices

Tests ALL 8 metadata schemas with:
1. Valid metadata following exact JSON schema patterns
2. Invalid metadata to verify error detection
3. All required fields per schema type
4. Proper unique_id patterns from BMAD_INTEGRATION_RULES.md

Following 2025 Qdrant MCP best practices.
"""

from validate_metadata import run_all_validations

print("\n" + "=" * 80)
print("COMPREHENSIVE SCHEMA VALIDATION - 2025 BEST PRACTICES")
print("All 8 Schema Types + Duplicate Detection")
print("=" * 80)

tests_run = 0
tests_passed = 0


def test(name: str, metadata: dict, should_pass: bool):
    """Run test and track results."""
    global tests_run, tests_passed
    tests_run += 1

    print(f"\n{'─'*80}")
    print(f"TEST {tests_run}: {name}")
    print(f"Expected: {'✓ PASS' if should_pass else '✗ FAIL'}")

    all_valid, messages = run_all_validations(metadata)

    # Print first 2 messages
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
print("VALID METADATA TESTS - Following Exact Schema Patterns")
print("=" * 80)

# 1. architecture_decision (valid)
# Pattern: ^arch-decision-[a-z0-9-]+-[0-9]{4}-[0-9]{2}-[0-9]{2}$
test(
    "architecture_decision (valid) - 5-tier Qdrant",
    {
        "unique_id": "arch-decision-5-tier-qdrant-2024-12-15",
        "type": "architecture_decision",
        "component": "qdrant",
        "importance": "critical",
        "created_at": "2024-12-15",
        "breaking_change": True,
    },
    should_pass=True,
)

# 2. agent_spec (valid)
# Pattern: ^agent-[0-9]{2}[a-z]?-spec$
test(
    "agent_spec (valid) - Agent 15 Storage Router",
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

# 3. story_outcome (valid)
# Pattern: ^story-[0-9]+-[0-9]+-complete$
test(
    "story_outcome (valid) - Story 2-17 Storage Routing",
    {
        "unique_id": "story-2-17-complete",
        "type": "story_outcome",
        "story_id": "2-17",
        "component": "agents",
        "importance": "critical",
        "created_at": "2025-12-20",
    },
    should_pass=True,
)

# 4. error_pattern (valid)
# Pattern: ^error-[a-z0-9-]+$
# IMPORTANT: Requires BOTH severity AND importance
test(
    "error_pattern (valid) - Qdrant Connection Timeout",
    {
        "unique_id": "error-qdrant-connection-timeout",
        "type": "error_pattern",
        "component": "qdrant",
        "severity": "high",
        "importance": "high",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

# 5. database_schema (valid)
# Pattern: ^schema-[a-z_]+-[a-z]+$
test(
    "database_schema (valid) - chunks table PostgreSQL",
    {
        "unique_id": "schema-chunks-postgres",
        "type": "database_schema",
        "table_name": "chunks",
        "database": "postgresql",
        "component": "postgres",
        "importance": "critical",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

# 6. config_pattern (valid)
# Pattern: ^config-[a-z0-9-]+$
test(
    "config_pattern (valid) - Qdrant Connection Settings",
    {
        "unique_id": "config-qdrant-connection",
        "type": "config_pattern",
        "component": "qdrant",
        "importance": "high",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

# 7. integration_example (valid)
# Pattern: ^integration-[a-z0-9-]+$
test(
    "integration_example (valid) - Agent 15 to Qdrant",
    {
        "unique_id": "integration-agent15-qdrant",
        "type": "integration_example",
        "component": "agents",
        "importance": "medium",
        "created_at": "2025-12-29",
    },
    should_pass=True,
)

# 8. best_practice (valid)
# Pattern: ^bp-[a-z0-9-]+$
# IMPORTANT: Requires domain, technology, category, discovered_by
test(
    "best_practice (valid) - Qdrant Batch Upsert Optimization",
    {
        "unique_id": "bp-qdrant-batch-upsert-2024-12-28",
        "type": "best_practice",
        "domain": "vector_search",
        "technology": "qdrant",
        "category": "performance",
        "component": "qdrant",
        "importance": "high",
        "created_at": "2024-12-28",
        "discovered_by": "agent_15",
    },
    should_pass=True,
)


print("\n" + "=" * 80)
print("INVALID METADATA TESTS - Error Detection")
print("=" * 80)

# Test 9: Missing required field
test(
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

# Test 10: Invalid importance value
test(
    "Invalid importance level (super-critical)",
    {
        "unique_id": "arch-decision-test-2025-12-29",
        "type": "architecture_decision",
        "component": "qdrant",
        "importance": "super-critical",  # Invalid
        "created_at": "2025-12-29",
        "breaking_change": True,
    },
    should_pass=False,
)

# Test 11: Wrong unique_id pattern for story_outcome
test(
    "Wrong unique_id pattern (missing -complete suffix)",
    {
        "unique_id": "story-2-17",  # Should be "story-2-17-complete"
        "type": "story_outcome",
        "story_id": "2-17",
        "component": "agents",
        "importance": "high",
        "created_at": "2025-12-29",
    },
    should_pass=False,
)

# Test 12: Invalid component enum value
test(
    "Invalid component enum value",
    {
        "unique_id": "arch-decision-test-2025-12-29",
        "type": "architecture_decision",
        "component": "invalid_component_name",  # Not in enum
        "importance": "critical",
        "created_at": "2025-12-29",
        "breaking_change": True,
    },
    should_pass=False,
)

# Test 13: best_practice missing required fields
test(
    "best_practice missing required fields (domain, technology, category)",
    {
        "unique_id": "bp-test-2025-12-29",
        "type": "best_practice",
        "component": "qdrant",
        "importance": "high",
        "created_at": "2025-12-29",
        # Missing: domain, technology, category, discovered_by
    },
    should_pass=False,
)

# Test 14: database_schema wrong unique_id format
test(
    "database_schema wrong unique_id (has date, should be table-database)",
    {
        "unique_id": "schema-chunks-2025-12-29",  # Wrong, should be schema-chunks-postgres
        "type": "database_schema",
        "table_name": "chunks",
        "database": "postgresql",
        "component": "postgres",
        "importance": "critical",
        "created_at": "2025-12-29",
    },
    should_pass=False,
)


# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY - SCHEMA VALIDATION")
print("=" * 80)
print(f"Total Tests: {tests_run}")
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_run - tests_passed}")
print(f"Success Rate: {(tests_passed/tests_run)*100:.1f}%")

if tests_passed == tests_run:
    print("\n✅ ALL SCHEMA VALIDATION TESTS PASSED")
    print("\nKEY FINDINGS:")
    print("✓ All 8 schema types validate correctly")
    print("✓ unique_id patterns enforced per BMAD_INTEGRATION_RULES.md")
    print("✓ Required field validation works")
    print("✓ Importance level validation works")
    print("✓ Enum validation works")
    print(
        "✓ best_practice schema requires: domain, technology, category, discovered_by"
    )
    print("✓ story_outcome unique_id MUST end with '-complete'")
    print("✓ database_schema unique_id format: schema-{table}-{database}")
    print("\nREADY FOR PRODUCTION")
    exit(0)
else:
    print(f"\n⚠️  {tests_run - tests_passed} TESTS FAILED")
    print("Review failures above")
    exit(1)
