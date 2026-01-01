# Validation Framework

> Scripts for validating, testing, and maintaining knowledge entries

## Overview

This folder contains all validation, testing, and maintenance scripts for the knowledge management system.

## Files

### Validation Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `validate_metadata.py` | Validate metadata against JSON schemas | Before storing entries |
| `pre_storage_validator.py` | Complete pre-storage validation | Automated validation pipeline |
| `check_duplicates.py` | Detect duplicate entries | Before bulk imports |

### Test Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_all_schemas.py` | Validate all JSON schemas | CI pipeline |
| `test_duplicate_detection.py` | Test duplicate detection logic | CI pipeline |
| `test_validation_comprehensive.py` | Full validation test suite | CI pipeline |
| `test_storage_workflow.py` | Test end-to-end storage | CI pipeline |
| `test_security_hardening.py` | Security validation tests | CI pipeline |
| `test_inventory_updates.py` | Test inventory tracking | CI pipeline |
| `test_monthly_review.py` | Test review workflow | CI pipeline |

### Utility Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `update_inventory.py` | Update tracking/knowledge_inventory.md | After storage operations |
| `run_all_tests.sh` | Run complete test suite | CI and local testing |
| `conftest.py` | Pytest configuration | Test infrastructure |

## Usage

### Running All Tests

```bash
# From project root
cd validation
bash run_all_tests.sh

# Or run individual tests
python test_all_schemas.py
python test_duplicate_detection.py
```

### Validating Metadata

```bash
# Validate with explicit type
python validation/validate_metadata.py \
  --metadata entry.json \
  --type architecture_decision

# Auto-detect type from metadata
python validation/validate_metadata.py \
  --metadata entry.json \
  --auto-detect
```

### Checking for Duplicates

```bash
# Check if entry already exists
python validation/check_duplicates.py \
  --content "Your knowledge content" \
  --collection bmad-knowledge
```

### Pre-Storage Validation

```bash
# Complete validation before storage
python validation/pre_storage_validator.py \
  --content "Knowledge content" \
  --metadata '{"unique_id": "...", "type": "...", ...}'
```

## Test Categories

### Schema Validation (`test_all_schemas.py`)

- Validates all JSON schemas are valid Draft-07
- Checks required fields are defined
- Verifies enum values are consistent

### Duplicate Detection (`test_duplicate_detection.py`)

- Content hash matching
- Semantic similarity detection
- unique_id collision detection

### Security (`test_security_hardening.py`)

- Input sanitization
- JSON depth limits (prevent ReDoS)
- Size limits (prevent memory exhaustion)
- Pattern validation (prevent injection)

### Storage Workflow (`test_storage_workflow.py`)

- End-to-end storage simulation
- Metadata transformation
- Error handling

## Customization

### Adding New Tests

1. Create `test_your_feature.py`
2. Use exit codes: `exit(0)` for pass, `exit(1)` for fail
3. Add to `run_all_tests.sh`

### Modifying Validation Rules

Edit `validate_metadata.py`:

```python
# Add new allowed types
ALLOWED_TYPES = [
    "architecture_decision",
    "your_new_type",  # Add here
]

# Adjust security limits
MAX_JSON_DEPTH = 100
MAX_JSON_SIZE = 1_000_000
```

### Custom Duplicate Detection

Edit `check_duplicates.py` to adjust:
- Similarity threshold (default: 0.95)
- Hash algorithm (default: SHA256)
- Comparison fields

## CI Integration

The `run_all_tests.sh` script is used in GitHub Actions:

```yaml
- name: Run tests
  run: |
    cd validation
    bash run_all_tests.sh
```

Test results are reported as exit codes:
- `0` - All tests passed
- `1` - One or more tests failed

## Related Documentation

- [metadata-schemas/](../metadata-schemas/) - JSON schemas for validation
- [BMAD_INTEGRATION_RULES.md](../BMAD_INTEGRATION_RULES.md) - Validation rules for agents
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Common validation errors
