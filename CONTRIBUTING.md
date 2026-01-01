# Contributing Guide

Thank you for your interest in contributing to Qdrant MCP Knowledge Management for BMAD!

## Ways to Contribute

- Report bugs and issues
- Suggest new features
- Improve documentation
- Submit pull requests
- Share your use cases

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR-USERNAME/bmad-qdrant-knowledge-management.git
cd bmad-qdrant-knowledge-management
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install qdrant-client python-dotenv pytest

# Copy environment file
cp .env.example .env
```

### 3. Start Qdrant for Testing

```bash
docker run -d --name qdrant-dev -p 6333:6333 qdrant/qdrant
```

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all public functions
- Keep functions focused and single-purpose

### Documentation

- Update README.md if adding new features
- Add docstrings to new functions
- Update relevant guide documents
- Use clear, concise language

### Testing

Before submitting:

```bash
# Run validation tests
python validation/test_all_schemas.py

# Test scripts work
python scripts/create_collections.py --check-only
```

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, documented code
- Add tests if applicable
- Update documentation as needed

### 3. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
# or
git commit -m "fix: resolve bug description"
```

Commit message prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Reporting Issues

When reporting issues, please include:

1. **Description** - What happened?
2. **Expected behavior** - What should have happened?
3. **Steps to reproduce** - How can we recreate the issue?
4. **Environment** - OS, Python version, Qdrant version
5. **Logs/Error messages** - Any relevant output

## Feature Requests

For feature requests, please describe:

1. **Use case** - What problem does this solve?
2. **Proposed solution** - How should it work?
3. **Alternatives** - Other approaches considered
4. **Additional context** - Screenshots, examples, etc.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## Questions?

- Open an issue for questions
- Check existing issues first
- Tag with `question` label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
