# 🧠 Engram MCP

**A zero-dependency, auto-decaying, pure SQLite MCP server for persistent AI agent memory.**

> *engram (noun): a hypothesized physical trace of memory stored in the brain — the biological basis of how memories persist.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)](#)
[![Protocol](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://modelcontextprotocol.io)

Engram is a fully local, lightning-fast memory layer for AI agents (Claude Code, Cursor, Windsurf, etc.) connected via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io). It is built entirely on the Python 3 standard library. No cloud API keys, no vector databases, no Docker, and no bloat.

---

## 🛑 The Problem: "Agent Amnesia"

If you use AI coding agents, you know the frustration: **every session starts completely fresh**. 
The agent doesn't remember that you prefer `pnpm` over `npm`, it forgets the architectural boundaries you agreed on yesterday, and it constantly asks you for the same context. 

Existing solutions try to fix this by bolting on massive Vector Databases (PostgreSQL/pgvector, Chroma, Pinecone) that require heavy dependencies, Docker containers, and expensive OpenAI API calls just to generate embeddings.

## 💡 The Solution: What is Engram MCP?

**Engram MCP** is a ruthlessly optimized, zero-dependency alternative. It uses standard **SQLite FTS5 (Full-Text Search)** to achieve blazing-fast keyword retrieval entirely locally. You simply drop the `server.py` script into your MCP configuration, and your agent instantly gains the ability to remember, recall, and manage its own long-term memory across sessions.

### Key Benefits

*   **Stop Repeating Yourself:** Teach your agent your preferences, tech stack, and architectural decisions *once*. It will automatically recall them on the next boot.
*   **Zero Infrastructure:** No databases to spin up. Engram automatically creates a local SQLite file in your home directory (`~/.engram-mcp/memory.db`).
*   **Zero API Costs:** Because it uses local BM25/FTS5 keyword indexing instead of semantic embeddings, you pay $0 in API credits for memory retrieval.
*   **Total Data Privacy:** Your codebase context and architectural secrets never leave your local machine.

---

## 🚀 Core Capabilities & Features

1.  **🐍 Zero Dependencies**
    Runs entirely on the Python Standard Library (`sqlite3`, `json`, `sys`, `hashlib`). No `pip install` required.
2.  **⏳ Intelligent Auto-Decay (Forgetting Mechanism)**
    Unlike other servers that hoard data forever, Engram prevents stale context poisoning by employing a background auto-decay algorithm:
    *   Whenever an agent searches or retrieves a memory, it automatically bumps the `access_count` and updates the `updated_at` timestamp.
    *   Whenever the MCP server spins up, it runs a background decay query: any memory that hasn't been accessed in 30 days automatically loses 1 point of `importance`.
    Your agent's context window stays clean, relevant, and self-maintaining without manual intervention.
3.  **🛡️ Enterprise-Grade Concurrency (WAL Mode)**
    Designed for multi-agent workflows. Engram implements SQLite Write-Ahead Logging (`PRAGMA journal_mode=WAL`) and strict connection timeouts. You can run Cursor and Claude Code simultaneously without triggering `database is locked` crashes.
4.  **🔒 Payload Bounding & Resilience**
    Engram strictly clamps memory outputs (max 8 results) to prevent LLM context-window blowouts, and truncates incoming memories to 8,000 characters to prevent payload bloat.
5.  **⌨️ Standalone CLI Manager**
    Comes with a built-in terminal tool (`engram.py`) so human developers can manually view, edit, search, or delete the agent's memories at any time.

---

## ⚙️ How It Works (Architecture)

```text
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
│  │ Auto-Decay │  │  WAL Mode Concurrency   │ │
│  └────────────┘  └─────────────────────────┘ │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│            memory.db (Local File)            │
│  ┌────────┐  ┌───────────┐  ┌────────────┐  │
│  │memories│  │memories_fts│  │  indexes   │  │
│  └────────┘  └───────────┘  └────────────┘  │
└──────────────────────────────────────────────┘
```

When an agent requests a memory, Engram performs a multi-pass FTS5 keyword search. If the syntax is malformed, it gracefully falls back to standard `LIKE` SQL queries. It deduplicates results, bumps the access timestamp, and returns a clamped array directly to the LLM.

---

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/lalithbuilds/engram-mcp.git
cd engram-mcp
```

### 2. Configure Your MCP Client
Add Engram to your MCP configuration file (e.g., `claude_desktop_config.json` or Cursor's MCP settings):

```json
{
  "mcpServers": {
    "engram": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/engram-mcp"
    }
  }
}
```

### 3. Done.
No virtual environments, no `requirements.txt`. Your agent will now automatically use the `memory_auto_context` tool when you start a new chat.

---

## 🛠️ The `engram` CLI Tool

You are always in control of what the agent remembers. You can use the bundled `engram.py` CLI to interact with the database yourself.

```bash
# Save a new memory for the agent manually
python3 engram.py save "We use Tailwind CSS for all styling, never raw CSS." --category frontend --importance 10

# Search what the agent knows about a topic
python3 engram.py search "Tailwind"

# List all memories in the database
python3 engram.py list

# Delete a specific memory by its ID
python3 engram.py delete abc123def456

# View database size and category breakdown
python3 engram.py stats
```

---

## 🤝 Contributing

We welcome contributions! Specifically, we are looking for help adding a `--json` export flag to the CLI. 
Check out our issues labeled `good first issue` to get started. See [CONTRIBUTING.md](https://github.com/lalithbuilds/engram-mcp/blob/main/CONTRIBUTING.md) for guidelines.

## 🐛 Troubleshooting

### Common Issues

**"DB not found at ~/.engram-mcp/memory.db. Run the MCP server first."**
- The SQLite database is created when the MCP server starts for the first time.
- Make sure you're running `server.py` before using the CLI.
- Check that the MCP server configuration points to the correct path.

**"database is locked" errors**
- This happens when multiple processes try to write to the database simultaneously.
- Engram uses WAL mode which handles most concurrency, but if you see this:
  - Wait a moment and try again (the lock is usually temporary).
  - Check if another `engram` process is running.
  - Restart the MCP server if the issue persists.

**MCP client fails to parse stdio output**
- The MCP server communicates via JSON-RPC over stdio.
- Ensure you're using Python 3.8+ (`python3 --version`).
- Check that the `server.py` path is correct in your MCP config.
- Try running `python3 server.py` directly to see if there are any Python errors.

**"Warning: fragment with name X already exists"**
- This is a warning about duplicate memory IDs, not an error.
- It typically means the same content was saved multiple times.
- Use `engram list` and `engram delete <id>` to remove duplicates.

### Getting Help

- Check the [GitHub Issues](https://github.com/lalithbuilds/engram-mcp/issues) for known problems.
- Open a new issue with:
  - Your Python version (`python3 --version`)
  - The exact error message
  - Steps to reproduce

## 📄 License

MIT — See [LICENSE](LICENSE) for details. Built by [Lalith Chandra](https://github.com/lalithbuilds).

---
*If Engram saves you from repeating yourself to an AI, consider giving it a ⭐!*