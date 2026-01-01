#!/usr/bin/env python3
"""
Pytest Configuration and Shared Fixtures

Following 2025 best practices:
- pytest fixtures for test isolation
- No global state
- Parallel test execution support (pytest-xdist)
"""

import pytest


@pytest.fixture
def test_counter():
    """
    Test counter fixture for tracking test results.

    Replaces global state pattern with proper test isolation.
    Each test function gets its own counter instance.

    Returns:
        TestCounter instance with run and passed attributes
    """

    class TestCounter:
        def __init__(self):
            self.run = 0
            self.passed = 0

        def increment(self, passed: bool = True):
            """Increment counters."""
            self.run += 1
            if passed:
                self.passed += 1

        def summary(self) -> dict:
            """Get test summary statistics."""
            return {
                "run": self.run,
                "passed": self.passed,
                "failed": self.run - self.passed,
                "success_rate": (
                    (self.passed / self.run * 100) if self.run > 0 else 0.0
                ),
            }

    return TestCounter()


@pytest.fixture
def assert_test(test_counter):
    """
    Custom assertion fixture with detailed output.

    Replaces the test() function pattern with pytest-compatible fixture.

    Args:
        test_counter: TestCounter fixture

    Returns:
        Callable that performs test assertion and tracking
    """

    def _assert(name: str, condition: bool, details: str = ""):
        """
        Assert condition and track result.

        Args:
            name: Test name/description
            condition: Boolean condition to test
            details: Optional details to print

        Raises:
            AssertionError: If condition is False
        """
        test_counter.increment(passed=condition)

        test_num = test_counter.run
        status = "✅ PASS" if condition else "❌ FAIL"

        print(f"\n{status} - TEST {test_num}: {name}")
        if details:
            print(f"   {details}")

        assert condition, f"{name} failed: {details}"

    return _assert


@pytest.fixture
def sample_metadata():
    """
    Sample metadata for testing.

    Returns:
        Dictionary with valid metadata structure
    """
    return {
        "unique_id": "arch-decision-5-tier-qdrant-2024-12-15",
        "type": "architecture_decision",
        "component": "qdrant",
        "importance": "critical",
        "created_at": "2024-12-15",
        "breaking_change": True,
    }


@pytest.fixture
def sample_entries():
    """
    Sample knowledge entries for inventory testing.

    Returns:
        List of sample entry dictionaries
    """
    return [
        {
            "unique_id": "arch-decision-5-tier-qdrant-2024-12-15",
            "type": "architecture_decision",
            "component": "qdrant",
            "importance": "critical",
            "created_at": "2024-12-15",
            "breaking_change": True,
            "keywords": ["qdrant", "architecture", "5-tier"],
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
    ]
