# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.0.0]: https://github.com/Hidden-History/bmad-qdrant-knowledge-management/releases/tag/v1.0.0
