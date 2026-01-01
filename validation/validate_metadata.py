#!/usr/bin/env python3
"""
Metadata Validation Script for Qdrant MCP Knowledge Management

Validates metadata against JSON schemas before storage.
Ensures all required fields are present and meet constraints.

Usage:
    python validate_metadata.py --metadata metadata.json --type architecture_decision
    python validate_metadata.py --metadata metadata.json --auto-detect
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple
from jsonschema import validate, ValidationError


# Path to schema directory
SCHEMA_DIR = Path(__file__).parent.parent / "metadata-schemas"

# Security: Limits to prevent ReDoS and memory exhaustion attacks
MAX_JSON_DEPTH = 100  # Prevent deeply nested JSON attacks
MAX_JSON_SIZE = 1_000_000  # 1MB limit for metadata

# Allowed knowledge types
ALLOWED_TYPES = [
    "architecture_decision",
    "agent_spec",
    "story_outcome",
    "error_pattern",
    "database_schema",
    "config_pattern",
    "integration_example",
    "best_practice",  # Agent-discovered best practices
]


def validate_json_safety(obj: Any, depth: int = 0) -> None:
    """
    Validate JSON structure is safe (not too deep, preventing ReDoS).

    Args:
        obj: JSON object to validate
        depth: Current recursion depth

    Raises:
        ValueError: If JSON is too deeply nested or structure is unsafe
    """
    if depth > MAX_JSON_DEPTH:
        raise ValueError(
            f"Security: JSON too deeply nested (max: {MAX_JSON_DEPTH} levels). "
            f"This prevents ReDoS attacks."
        )

    if isinstance(obj, dict):
        for key, value in obj.items():
            validate_json_safety(value, depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            validate_json_safety(item, depth + 1)


def load_schema(knowledge_type: str) -> Dict[str, Any]:
    """
    Load JSON schema for specified knowledge type.

    Args:
        knowledge_type: Type of knowledge (e.g., 'architecture_decision')

    Returns:
        Loaded JSON schema dictionary

    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file is invalid JSON
    """
    schema_file = SCHEMA_DIR / f"{knowledge_type}.json"

    if not schema_file.exists():
        raise FileNotFoundError(
            f"Schema file not found: {schema_file}\n"
            f"Available types: {', '.join(ALLOWED_TYPES)}"
        )

    with open(schema_file, "r") as f:
        return json.load(f)


def validate_metadata(
    metadata: Dict[str, Any], knowledge_type: str = None
) -> Tuple[bool, str]:
    """
    Validate metadata against JSON schema.

    Args:
        metadata: Metadata dictionary to validate
        knowledge_type: Optional type override (auto-detected from metadata['type'] if not provided)

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    # Security: Check JSON size (prevent memory exhaustion)
    try:
        json_str = json.dumps(metadata)
        if len(json_str) > MAX_JSON_SIZE:
            return False, (
                f"ERROR: Metadata too large ({len(json_str):,} bytes).\n"
                f"Maximum allowed: {MAX_JSON_SIZE:,} bytes (1MB).\n"
                f"This prevents memory exhaustion attacks."
            )
    except (TypeError, ValueError) as e:
        return False, f"ERROR: Metadata is not JSON serializable: {e}"

    # Security: Check JSON depth (prevent ReDoS)
    try:
        validate_json_safety(metadata)
    except ValueError as e:
        return False, f"ERROR: {e}"

    # Auto-detect type if not provided
    if knowledge_type is None:
        if "type" not in metadata:
            return False, "ERROR: metadata['type'] field is required for auto-detection"
        knowledge_type = metadata["type"]

    # Validate type is allowed
    if knowledge_type not in ALLOWED_TYPES:
        return False, (
            f"ERROR: Invalid type '{knowledge_type}'\n"
            f"Allowed types: {', '.join(ALLOWED_TYPES)}"
        )

    # Load schema
    try:
        schema = load_schema(knowledge_type)
    except FileNotFoundError as e:
        return False, str(e)
    except json.JSONDecodeError as e:
        return False, f"ERROR: Schema file is invalid JSON: {e}"

    # Validate against schema
    try:
        validate(instance=metadata, schema=schema)
        return True, f"✓ Metadata valid for type '{knowledge_type}'"
    except ValidationError as e:
        error_path = " → ".join([str(p) for p in e.path]) if e.path else "root"
        return False, (
            f"ERROR: Metadata validation failed\n"
            f"Path: {error_path}\n"
            f"Message: {e.message}\n"
            f"Schema rule: {e.schema.get('description', 'No description')}"
        )


def validate_required_fields(metadata: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that all critical required fields are present.

    This is a quick check before full schema validation.

    Args:
        metadata: Metadata dictionary

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    required_fields = ["unique_id", "type", "component", "importance", "created_at"]
    missing_fields = [field for field in required_fields if field not in metadata]

    if missing_fields:
        return False, (
            f"ERROR: Missing required fields: {', '.join(missing_fields)}\n"
            f"Required fields: {', '.join(required_fields)}"
        )

    return True, "✓ All critical required fields present"


def validate_importance_level(metadata: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate importance level is one of allowed values.

    Args:
        metadata: Metadata dictionary

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    allowed_importance = ["critical", "high", "medium", "low"]
    importance = metadata.get("importance")

    if importance not in allowed_importance:
        return False, (
            f"ERROR: Invalid importance level '{importance}'\n"
            f"Allowed values: {', '.join(allowed_importance)}"
        )

    return True, f"✓ Importance level '{importance}' is valid"


def validate_unique_id_format(metadata: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate unique_id follows expected format for type.

    Args:
        metadata: Metadata dictionary

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    unique_id = metadata.get("unique_id", "")
    knowledge_type = metadata.get("type", "")

    # Expected prefixes for each type
    expected_prefixes = {
        "architecture_decision": "arch-decision-",
        "agent_spec": "agent-",
        "story_outcome": "story-",
        "error_pattern": "error-",
        "database_schema": "schema-",
        "config_pattern": "config-",
        "integration_example": "integration-",
        "best_practice": "bp-",  # Format: bp-{technology}-{topic}-{YYYY-MM-DD}
    }

    expected_prefix = expected_prefixes.get(knowledge_type)
    if expected_prefix and not unique_id.startswith(expected_prefix):
        return False, (
            f"WARNING: unique_id '{unique_id}' doesn't follow expected format\n"
            f"Expected prefix: '{expected_prefix}'\n"
            f"Example: {expected_prefix}example-name"
        )

    return True, f"✓ unique_id format matches type '{knowledge_type}'"


def run_all_validations(
    metadata: Dict[str, Any], knowledge_type: str = None
) -> Tuple[bool, list]:
    """
    Run all validation checks on metadata.

    Args:
        metadata: Metadata dictionary
        knowledge_type: Optional type override

    Returns:
        Tuple of (all_valid: bool, messages: list)
    """
    results = []
    all_valid = True

    # Quick checks first
    checks = [
        ("Required Fields", validate_required_fields),
        ("Importance Level", validate_importance_level),
        ("Unique ID Format", validate_unique_id_format),
    ]

    for check_name, check_func in checks:
        is_valid, message = check_func(metadata)
        results.append(f"{check_name}: {message}")
        if not is_valid and "ERROR" in message:
            all_valid = False

    # Full schema validation
    is_valid, message = validate_metadata(metadata, knowledge_type)
    results.append(f"Schema Validation: {message}")
    if not is_valid:
        all_valid = False

    return all_valid, results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate metadata against Qdrant MCP knowledge schemas"
    )
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON file")
    parser.add_argument(
        "--type",
        choices=ALLOWED_TYPES,
        help="Knowledge type (auto-detected from metadata if not provided)",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Fail on warnings (not just errors)"
    )

    args = parser.parse_args()

    # Load metadata
    try:
        with open(args.metadata, "r") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Metadata file not found: {args.metadata}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in metadata file: {e}")
        sys.exit(1)

    # Run validations
    all_valid, messages = run_all_validations(metadata, args.type)

    # Print results
    print("\n" + "=" * 60)
    print("METADATA VALIDATION RESULTS")
    print("=" * 60 + "\n")

    for message in messages:
        print(message)

    print("\n" + "=" * 60)

    # Determine exit code
    if not all_valid:
        print("❌ VALIDATION FAILED")
        sys.exit(1)
    elif args.strict and any("WARNING" in msg for msg in messages):
        print("⚠️  VALIDATION PASSED WITH WARNINGS (strict mode)")
        sys.exit(1)
    else:
        print("✅ VALIDATION PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
