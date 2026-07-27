# Security Policy

## Supported Versions

| Version | Supported |
|:--------|:---------:|
| 1.x     | ✅ Yes    |
| < 1.0   | ❌ No     |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Email: lalith070804@gmail.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours and aim to patch within 7 days.

## Security Model

Engram MCP is a **fully local** tool. It:
- Stores all data in a local SQLite file (`~/engram-mcp/memory.db`)
- Never makes network requests
- Never sends data to any external service
- Has zero third-party dependencies

The primary security consideration is filesystem access: the database file is readable by any process running as the same user.
