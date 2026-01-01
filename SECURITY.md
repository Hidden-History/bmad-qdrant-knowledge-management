# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:

1. **GitHub Issues**: Open an issue with the `security` label
2. **Email**: Contact the repository owner directly

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- Initial response: Within 48 hours
- Status update: Within 7 days
- Resolution target: Within 30 days (depending on severity)

## Security Best Practices

When using this template:

### Environment Variables

- Never commit `.env` files with real credentials
- Use `.env.example` as a template only
- Store production credentials in secure secret management

### Qdrant Configuration

- Use authentication in production (`QDRANT_API_KEY`)
- Enable TLS for remote Qdrant instances
- Restrict network access to Qdrant ports

### Knowledge Base Content

- Do not store sensitive data (passwords, API keys, PII)
- Review content before storing to avoid credential leaks
- Use `group_id` for tenant isolation in multi-user setups

## Dependencies

This project uses:
- `qdrant-client` - Official Qdrant Python client
- `jsonschema` - JSON Schema validation
- `python-dotenv` - Environment variable loading

Keep dependencies updated to receive security patches.
