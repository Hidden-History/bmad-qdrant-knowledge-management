#!/usr/bin/env python3
"""
Knowledge Inventory Update Script

Automatically updates tracking/knowledge_inventory.md with current
knowledge base statistics and entries.

Following 2025 best practices for Qdrant MCP governance.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Security: Define allowed base directory for path traversal prevention
# Can be overridden for testing via environment variable
import os

_default_base = Path(__file__).parent.parent / "tracking"
ALLOWED_BASE_DIR = Path(os.getenv("QDRANT_INVENTORY_BASE_DIR", str(_default_base)))


def generate_inventory_markdown(entries: List[Dict]) -> str:
    """Generate the complete inventory markdown from knowledge entries."""

    # Calculate statistics
    total = len(entries)
    by_type = {}
    by_component = {}
    by_importance = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    deprecated_count = 0
    last_created = None

    # Group entries
    for entry in entries:
        # By type
        entry_type = entry.get("type", "unknown")
        if entry_type not in by_type:
            by_type[entry_type] = {
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            }
        by_type[entry_type]["total"] += 1
        importance = entry.get("importance", "medium")
        by_type[entry_type][importance] += 1
        by_importance[importance] += 1

        # By component
        component = entry.get("component", "unknown")
        by_component[component] = by_component.get(component, 0) + 1

        # Track deprecated
        if entry.get("deprecated", False):
            deprecated_count += 1

        # Track last created
        created = entry.get("created_at")
        if created and (not last_created or created > last_created):
            last_created = created

    # Build markdown
    md = []
    md.append("# Qdrant MCP Knowledge Inventory")
    md.append("")
    md.append(
        "**Purpose**: Auto-updated tracking of all knowledge stored in Qdrant MCP"
    )
    md.append(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 📊 Summary Statistics")
    md.append("")
    md.append(f"- **Total Entries**: {total}")
    md.append(f"- **Last Entry Added**: {last_created or 'N/A'}")
    md.append(f"- **Deprecated**: {deprecated_count}")
    md.append("")
    md.append("### By Type")
    md.append("")
    md.append("| Type | Count | Critical | High | Medium | Low |")
    md.append("|------|-------|----------|------|--------|-----|")

    type_labels = {
        "architecture_decision": "Architecture Decisions",
        "agent_spec": "Agent Specifications",
        "story_outcome": "Story Outcomes",
        "error_pattern": "Error Patterns",
        "database_schema": "Database Schemas",
        "config_pattern": "Config Patterns",
        "integration_example": "Integration Examples",
        "best_practice": "Best Practices",
    }

    for type_key, type_label in type_labels.items():
        stats = by_type.get(
            type_key, {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
        )
        md.append(
            f"| {type_label} | {stats['total']} | {stats['critical']} | {stats['high']} | {stats['medium']} | {stats['low']} |"
        )

    md.append("")
    md.append("### By Component")
    md.append("")
    md.append("| Component | Count |")
    md.append("|-----------|-------|")

    for component in [
        "qdrant",
        "postgres",
        "neo4j",
        "agents",
        "docker",
        "api",
        "general",
    ]:
        count = by_component.get(component, 0)
        md.append(f"| {component} | {count} |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 🗂️ Detailed Inventory")
    md.append("")

    # Detailed sections for each type
    md.extend(_generate_arch_decisions_table(entries))
    md.extend(_generate_agent_specs_table(entries))
    md.extend(_generate_story_outcomes_table(entries))
    md.extend(_generate_error_patterns_table(entries))
    md.extend(_generate_database_schemas_table(entries))
    md.extend(_generate_config_patterns_table(entries))
    md.extend(_generate_integration_examples_table(entries))

    # Update log
    md.append("")
    md.append("## 📝 Update Log")
    md.append("")
    md.append(f"### {datetime.now().strftime('%Y-%m-%d')}")
    md.append(f"- Updated inventory: {total} total entries")
    md.append("")
    md.append("---")
    md.append("")

    # Keywords
    keywords = set()
    for entry in entries:
        if "keywords" in entry:
            keywords.update(entry["keywords"])

    md.append("## 🔍 Search Index")
    md.append("")
    md.append("**Keywords**: (Auto-generated from all entries)")
    md.append("")
    if keywords:
        for keyword in sorted(keywords)[:50]:  # Limit to top 50
            md.append(f"- {keyword}")
    else:
        md.append("- No entries yet")

    md.append("")
    md.append("---")
    md.append("")

    # Deprecated entries
    deprecated_entries = [e for e in entries if e.get("deprecated", False)]
    md.append("## ⚠️ Deprecated Entries")
    md.append("")
    md.append(f"**Count**: {len(deprecated_entries)}")
    md.append("")
    md.append("| unique_id | Type | Deprecated Date | Superseded By | Reason |")
    md.append("|-----------|------|-----------------|---------------|--------|")
    if deprecated_entries:
        for entry in deprecated_entries[:10]:  # Limit to 10 most recent
            unique_id = entry.get("unique_id", "-")
            entry_type = entry.get("type", "-")
            deprecated_date = entry.get("deprecated_date", "-")
            superseded_by = entry.get("superseded_by", "-")
            reason = entry.get("deprecation_reason", "-")[:50]
            md.append(
                f"| {unique_id} | {entry_type} | {deprecated_date} | {superseded_by} | {reason} |"
            )
    else:
        md.append("| - | - | - | - | - |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("**Auto-Update Script**: `validation/update_inventory.py`")
    md.append("**Next Scheduled Update**: After next knowledge entry")
    md.append("")

    return "\n".join(md)


def _generate_arch_decisions_table(entries: List[Dict]) -> List[str]:
    """Generate architecture decisions section."""
    filtered = [e for e in entries if e.get("type") == "architecture_decision"]
    md = [
        "### Architecture Decisions",
        "",
        f"**Count**: {len(filtered)}",
        "",
        "| unique_id | Component | Breaking | Importance | Created | Status |",
        "|-----------|-----------|----------|------------|---------|--------|",
    ]

    if filtered:
        for entry in filtered[:20]:  # Limit to 20 most recent
            unique_id = entry.get("unique_id", "-")
            component = entry.get("component", "-")
            breaking = "Yes" if entry.get("breaking_change", False) else "No"
            importance = entry.get("importance", "-")
            created = entry.get("created_at", "-")
            status = "Deprecated" if entry.get("deprecated", False) else "Active"
            md.append(
                f"| {unique_id} | {component} | {breaking} | {importance} | {created} | {status} |"
            )
    else:
        md.append("| - | - | - | - | - | - |")

    md.extend(["", "---", ""])
    return md


def _generate_agent_specs_table(entries: List[Dict]) -> List[str]:
    """Generate agent specifications section."""
    filtered = [e for e in entries if e.get("type") == "agent_spec"]
    md = [
        "### Agent Specifications",
        "",
        f"**Count**: {len(filtered)}",
        "",
        "| unique_id | Agent ID | Agent Name | Importance | Created | Status |",
        "|-----------|----------|------------|------------|---------|--------|",
    ]

    if filtered:
        for entry in filtered[:20]:
            unique_id = entry.get("unique_id", "-")
            agent_id = entry.get("agent_id", "-")
            agent_name = entry.get("agent_name", "-")
            importance = entry.get("importance", "-")
            created = entry.get("created_at", "-")
            status = "Deprecated" if entry.get("deprecated", False) else "Active"
            md.append(
                f"| {unique_id} | {agent_id} | {agent_name} | {importance} | {created} | {status} |"
            )
    else:
        md.append("| - | - | - | - | - | - |")

    md.extend(["", "---", ""])
    return md


def _generate_story_outcomes_table(entries: List[Dict]) -> List[str]:
    """Generate story outcomes section."""
    filtered = [e for e in entries if e.get("type") == "story_outcome"]
    md = [
        "### Story Outcomes",
        "",
        f"**Count**: {len(filtered)}",
        "",
        "| unique_id | Story ID | Epic | Importance | Created | Status |",
        "|-----------|----------|------|------------|---------|--------|",
    ]

    if filtered:
        for entry in filtered[:20]:
            unique_id = entry.get("unique_id", "-")
            story_id = entry.get("story_id", "-")
            epic = entry.get("epic_id", "-")
            importance = entry.get("importance", "-")
            created = entry.get("created_at", "-")
            status = "Deprecated" if entry.get("deprecated", False) else "Active"
            md.append(
                f"| {unique_id} | {story_id} | {epic} | {importance} | {created} | {status} |"
            )
    else:
        md.append("| - | - | - | - | - | - |")

    md.extend(["", "---", ""])
    return md


def _generate_error_patterns_table(entries: List[Dict]) -> List[str]:
    """Generate error patterns section."""
    filtered = [e for e in entries if e.get("type") == "error_pattern"]
    md = [
        "### Error Patterns",
        "",
        f"**Count**: {len(filtered)}",
        "",
        "| unique_id | Component | Severity | Created | Status |",
        "|-----------|-----------|----------|---------|--------|",
    ]

    if filtered:
        for entry in filtered[:20]:
            unique_id = entry.get("unique_id", "-")
            component = entry.get("component", "-")
            severity = entry.get("severity", "-")
            created = entry.get("created_at", "-")
            status = "Resolved" if entry.get("resolved", False) else "Active"
            md.append(
                f"| {unique_id} | {component} | {severity} | {created} | {status} |"
            )
    else:
        md.append("| - | - | - | - | - |")

    md.extend(["", "---", ""])
    return md


def _generate_database_schemas_table(entries: List[Dict]) -> List[str]:
    """Generate database schemas section."""
    filtered = [e for e in entries if e.get("type") == "database_schema"]
    md = [
        "### Database Schemas",
        "",
        f"**Count**: {len(filtered)}",
        "",
        "| unique_id | Table | Database | Created | Status |",
        "|-----------|-------|----------|---------|--------|",
    ]

    if filtered:
        for entry in filtered[:20]:
            unique_id = entry.get("unique_id", "-")
            table = entry.get("table_name", "-")
            database = entry.get("database", "-")
            created = entry.get("created_at", "-")
            status = "Deprecated" if entry.get("deprecated", False) else "Active"
            md.append(f"| {unique_id} | {table} | {database} | {created} | {status} |")
    else:
        md.append("| - | - | - | - | - |")

    md.extend(["", "---", ""])
    return md


def _generate_config_patterns_table(entries: List[Dict]) -> List[str]:
    """Generate config patterns section."""
    filtered = [e for e in entries if e.get("type") == "config_pattern"]
    md = [
        "### Config Patterns",
        "",
        f"**Count**: {len(filtered)}",
        "",
        "| unique_id | Component | Importance | Created | Status |",
        "|-----------|-----------|------------|---------|--------|",
    ]

    if filtered:
        for entry in filtered[:20]:
            unique_id = entry.get("unique_id", "-")
            component = entry.get("component", "-")
            importance = entry.get("importance", "-")
            created = entry.get("created_at", "-")
            status = "Deprecated" if entry.get("deprecated", False) else "Active"
            md.append(
                f"| {unique_id} | {component} | {importance} | {created} | {status} |"
            )
    else:
        md.append("| - | - | - | - | - |")

    md.extend(["", "---", ""])
    return md


def _generate_integration_examples_table(entries: List[Dict]) -> List[str]:
    """Generate integration examples section."""
    filtered = [e for e in entries if e.get("type") == "integration_example"]
    md = [
        "### Integration Examples",
        "",
        f"**Count**: {len(filtered)}",
        "",
        "| unique_id | Component | Importance | Created | Status |",
        "|-----------|-----------|------------|---------|--------|",
    ]

    if filtered:
        for entry in filtered[:20]:
            unique_id = entry.get("unique_id", "-")
            component = entry.get("component", "-")
            importance = entry.get("importance", "-")
            created = entry.get("created_at", "-")
            status = "Deprecated" if entry.get("deprecated", False) else "Active"
            md.append(
                f"| {unique_id} | {component} | {importance} | {created} | {status} |"
            )
    else:
        md.append("| - | - | - | - | - |")

    md.extend(["", "---", ""])
    return md


def update_inventory(entries: List[Dict], output_path: str = None) -> str:
    """
    Update the knowledge inventory markdown file.

    Args:
        entries: List of knowledge entry metadata dicts
        output_path: Path to write inventory file (default: ../tracking/knowledge_inventory.md)

    Returns:
        The generated markdown content

    Raises:
        ValueError: If output_path is outside allowed directory (prevents path traversal)
    """
    markdown = generate_inventory_markdown(entries)

    if output_path:
        path = Path(output_path).resolve()

        # Security: Validate path is within allowed directory (CVE-2025-47273 prevention)
        try:
            path.relative_to(ALLOWED_BASE_DIR.resolve())
        except ValueError:
            raise ValueError(
                f"Security: Invalid path '{output_path}'. "
                f"Must be within allowed directory: {ALLOWED_BASE_DIR}"
            )

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown)
        print(f"✓ Inventory updated: {output_path}")

    return markdown


if __name__ == "__main__":
    print("Knowledge Inventory Update Script")
    print("Use update_inventory(entries, output_path) to generate inventory")
    print("This script is meant to be imported and called, not run directly")
