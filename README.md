# 🧠 Engram MCP

**A zero-dependency, stdlib-only MCP server for persistent AI agent memory.**

> *engram (noun): a hypothesized physical trace of memory stored in the brain — the biological basis of how memories persist.*

Built on pure Python 3 standard library. No cloud. No bloat. Just fast, local, full-text-searchable memory for your AI agents via the [Model Context Protocol](https://modelcontextprotocol.io).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)](#)
[![MCP](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://modelcontextprotocol.io)

---

## Why This Exists

Every AI agent forgets everything the moment a session ends. Commercial solutions like Mem0 or Qdrant add network latency, disk corruption risk, and heavy dependencies.

**Engram MCP** takes the opposite approach:
- **Zero third-party dependencies** — runs on Python's stdlib (`sqlite3`, `json`, `hashlib`)
- **FTS5 full-text search** with automatic `LIKE` fallback
- **~200 lines of server code** — auditable in minutes
- **Auto-initializing** — clones and runs instantly, no setup required
- **Input-hardened** — safe against malformed types, SQL injection, and oversized payloads

## Features

| Tool | Description |
|:---|:---|
| `memory_auto_context` | Session boot — returns top-ranked memories by importance. Call once at start. |
| `memory_smart_search` | Multi-pass FTS5 keyword search with deduplication and `LIKE` fallback. |
| `memory_save` | Save a memory with category, tags, and importance (1–10). Auto-deduplicates. |
| `memory_extract_save` | Bulk-save a text block as memory. Designed for session-end extraction. |
| `memory_delete` | Remove a memory by its unique 12-char SHA1 ID. |
| `memory_stats` | Database stats: total count, category breakdown, file size. |

## Architecture

```
┌──────────────────────────────────────────────┐
│              AI Agent / LLM                  │
│         (Claude, Gemini, GPT, etc.)          │
└──────────────┬───────────────────────────────┘
               │  JSON-RPC 2.0 over STDIO
               ▼
┌──────────────────────────────────────────────┐
│         Engram MCP Server (server.py)        │
│  ┌────────────┐  ┌─────────────────────────┐ │
│  │ Tool Router│  │  SQLite3 + FTS5 Engine  │ │
│  └────────────┘  └─────────────────────────┘ │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│            memory.db (SQLite WAL)            │
│  ┌────────┐  ┌───────────┐  ┌────────────┐  │
│  │memories│  │memories_fts│  │  indexes   │  │
│  └────────┘  └───────────┘  └────────────┘  │
└──────────────────────────────────────────────┘
```

## Quick Start

### 1. Clone

```bash
git clone https://github.com/lalithbuilds/engram-mcp.git
cd engram-mcp
```

### 2. Configure Your MCP Client

Add to your MCP client config (e.g., `mcp_config.json`):

```json
{
  "mcpServers": {
    "engram": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/path/to/engram-mcp"
    }
  }
}
```

### 3. Done

No `pip install`. No `requirements.txt`. No virtual environment. It just works.

## CLI Tool

A standalone terminal utility is included for human interaction:

```bash
# Save a memory
python3 ray-mem.py save "FastAPI runs on port 8000" --category project --importance 8

# Search memories
python3 ray-mem.py search "FastAPI"

# Recall top memories (session boot)
python3 ray-mem.py recall --limit 5

# List all memories
python3 ray-mem.py list

# Database stats
python3 ray-mem.py stats

# Delete by ID
python3 ray-mem.py delete abc123def456
```

## Test Results (v4.1)

```
✅ INIT              ✅ TOOLS_LIST        ✅ STATS
✅ SEARCH            ✅ SAVE              ✅ CONTEXT
✅ EMPTY_QUERY       ✅ UNKNOWN_TOOL      ✅ SQL_INJECTION
✅ STRING_IMPORTANCE ✅ STRING_LIMIT      ✅ NEGATIVE_IMP
✅ HUGE_IMPORTANCE   ✅ UNICODE/EMOJI     ✅ EMPTY_SAVE
✅ EMPTY_DELETE      ✅ EXTRACT_EMPTY     ✅ NEWLINES

18/18 PASSED — 0 FAILED
```

## Design Philosophy

This project follows the **Ponytail Coding Philosophy**:
- **YAGNI** — You Aren't Gonna Need It. No feature creep.
- **Stdlib First** — If the standard library can do it, use it.
- **Delete > Add** — Less code = fewer bugs.
- **Zero Cloud** — Your memory stays on your machine.

## Requirements

- Python 3.8+
- That's it. Seriously.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — See [LICENSE](LICENSE) for details.

---

*If you find this useful, consider giving it a ⭐ — it helps others discover the project.*

*Built by [Lalith Chandra](https://github.com/lalithbuilds)*