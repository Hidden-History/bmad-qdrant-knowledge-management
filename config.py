"""
Qdrant MCP Knowledge Management - Configuration Module

Centralized configuration for all scripts. All configurable values are loaded
from environment variables with sensible defaults.

Usage:
    from config import QDRANT_URL, KNOWLEDGE_COLLECTION, BEST_PRACTICES_COLLECTION
"""
import os
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly


# =============================================================================
# QDRANT CONNECTION
# =============================================================================

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

# =============================================================================
# COLLECTION NAMES
# Customize these for your project by setting environment variables
# =============================================================================

KNOWLEDGE_COLLECTION = os.getenv("QDRANT_KNOWLEDGE_COLLECTION", "bmad-knowledge")
BEST_PRACTICES_COLLECTION = os.getenv("QDRANT_BEST_PRACTICES_COLLECTION", "bmad-best-practices")

# =============================================================================
# EMBEDDING CONFIGURATION
# =============================================================================

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))

# =============================================================================
# PROJECT METADATA
# =============================================================================

PROJECT_NAME = os.getenv("PROJECT_NAME", "bmad-project")

# =============================================================================
# PATHS
# =============================================================================

ROOT_DIR = Path(__file__).parent
SCHEMAS_DIR = ROOT_DIR / "metadata-schemas"
VALIDATION_DIR = ROOT_DIR / "validation"
TRACKING_DIR = ROOT_DIR / "tracking"
EXAMPLES_DIR = ROOT_DIR / "examples"
SCRIPTS_DIR = ROOT_DIR / "scripts"

# =============================================================================
# KNOWLEDGE TYPES
# These are the allowed types for knowledge entries
# =============================================================================

ALLOWED_TYPES = [
    "architecture_decision",
    "agent_spec",
    "story_outcome",
    "error_pattern",
    "database_schema",
    "config_pattern",
    "integration_example",
    "best_practice",
]

# =============================================================================
# VALIDATION SETTINGS
# =============================================================================

# Minimum content length for knowledge entries
MIN_CONTENT_LENGTH = int(os.getenv("MIN_CONTENT_LENGTH", "100"))

# Maximum content length for knowledge entries
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "50000"))

# Semantic similarity threshold for duplicate detection
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))

# =============================================================================
# IMPORTANCE LEVELS
# =============================================================================

IMPORTANCE_LEVELS = ["critical", "high", "medium", "low"]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_collection_for_type(knowledge_type: str) -> str:
    """
    Route knowledge to the appropriate collection based on type.

    Args:
        knowledge_type: The type of knowledge being stored

    Returns:
        Collection name to use for storage
    """
    if knowledge_type == "best_practice":
        return BEST_PRACTICES_COLLECTION
    return KNOWLEDGE_COLLECTION


def validate_config() -> dict:
    """
    Validate configuration and return status.

    Returns:
        Dictionary with validation results
    """
    issues = []

    if not QDRANT_URL:
        issues.append("QDRANT_URL is not set")

    if not KNOWLEDGE_COLLECTION:
        issues.append("QDRANT_KNOWLEDGE_COLLECTION is not set")

    if EMBEDDING_DIMENSION <= 0:
        issues.append("EMBEDDING_DIMENSION must be positive")

    if MIN_CONTENT_LENGTH < 0:
        issues.append("MIN_CONTENT_LENGTH cannot be negative")

    if SIMILARITY_THRESHOLD < 0 or SIMILARITY_THRESHOLD > 1:
        issues.append("SIMILARITY_THRESHOLD must be between 0 and 1")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "config": {
            "qdrant_url": QDRANT_URL,
            "knowledge_collection": KNOWLEDGE_COLLECTION,
            "best_practices_collection": BEST_PRACTICES_COLLECTION,
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimension": EMBEDDING_DIMENSION,
            "project_name": PROJECT_NAME,
        }
    }


if __name__ == "__main__":
    # Print current configuration when run directly
    result = validate_config()
    print("Configuration Status:")
    print(f"  Valid: {result['valid']}")
    if result['issues']:
        print("  Issues:")
        for issue in result['issues']:
            print(f"    - {issue}")
    print("\nCurrent Configuration:")
    for key, value in result['config'].items():
        # Mask API key if present
        if 'api_key' in key.lower() and value:
            value = value[:4] + "..." + value[-4:] if len(value) > 8 else "****"
        print(f"  {key}: {value}")
