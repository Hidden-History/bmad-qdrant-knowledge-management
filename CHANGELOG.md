# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-01-01

### Added

- README files for all code folders:
  - `examples/README.md` - Search and store usage patterns
  - `metadata-schemas/README.md` - JSON schema documentation
  - `validation/README.md` - Testing and validation framework
  - `tracking/README.md` - Knowledge inventory templates

## [1.2.0] - 2026-01-01

### Added

- "About This Template" section in README explaining:
  - This is a real system used in production daily
  - Why it was built (solving AI memory/context problems)
  - Step-by-step guide for using the template
  - Customization table showing what to change
  - Clarification that this is a starter template, not a library
- Quick Links table now includes link to About section

## [1.1.1] - 2026-01-01

### Fixed

- Fixed Qdrant health check endpoint in CI (`/` instead of `/health`)
- Fixed ruff linting configuration to use `[tool.ruff.lint]` section
- Relaxed linting rules for example scripts (F401 unused imports, F541 f-strings)
- Fixed test runner to use `run_all_tests.sh` instead of pytest

## [1.1.0] - 2026-01-01

### Added

- GitHub Actions CI workflow with Python 3.9-3.12 testing
- Docker Compose configuration for one-command Qdrant setup
- Python packaging with `pyproject.toml` and `requirements.txt`
- Issue templates (bug report, feature request)
- Pull request template
- `CODE_OF_CONDUCT.md` - Contributor Covenant
- `SECURITY.md` - Security policy and best practices
- `CHANGELOG.md` - Version history
- Demo knowledge entries with example metadata
- Social preview image for GitHub sharing
- CI badge in README

### Changed

- Updated installation docs to use `docker compose up -d`
- Updated prerequisites to Python 3.9+
- Updated QUICKSTART with Docker Compose as recommended option

### Fixed

- Corrected git clone URL in README

## [1.0.0] - 2026-01-01

### Added

- Initial release of BMAD Qdrant Knowledge Management Template
- 8 metadata schemas for knowledge types:
  - `architecture_decision` - Major design choices
  - `agent_spec` - Agent capabilities and integration
  - `story_outcome` - Completed implementations
  - `error_pattern` - Problems and solutions
  - `database_schema` - Table structures
  - `config_pattern` - Configuration examples
  - `integration_example` - Working code patterns
  - `best_practice` - Universal patterns
- Validation framework with JSON Schema validation
- Duplicate detection system
- BMAD integration rules for agents
- Example population scripts
- Docker Compose setup for Qdrant
- GitHub Actions CI workflow
- Comprehensive documentation:
  - QUICKSTART.md - 15-minute setup guide
  - CONFIGURATION.md - All configuration options
  - ARCHITECTURE.md - System design
  - TROUBLESHOOTING.md - Common issues
  - BMAD_INTEGRATION_RULES.md - Agent enforcement rules
- Multitenancy support via `group_id` payload filtering
- Qdrant optimization guide in README

### Security

- Input validation on all metadata fields
- No credentials stored in repository
- Environment variable configuration

[1.2.1]: https://github.com/Hidden-History/bmad-qdrant-knowledge-management/releases/tag/v1.2.1
[1.2.0]: https://github.com/Hidden-History/bmad-qdrant-knowledge-management/releases/tag/v1.2.0
[1.1.1]: https://github.com/Hidden-History/bmad-qdrant-knowledge-management/releases/tag/v1.1.1
[1.1.0]: https://github.com/Hidden-History/bmad-qdrant-knowledge-management/releases/tag/v1.1.0
[1.0.0]: https://github.com/Hidden-History/bmad-qdrant-knowledge-management/releases/tag/v1.0.0
