# 🧠 Engram MCP

**A zero-dependency, auto-decaying, pure SQLite MCP server for persistent AI agent memory.**

*Built in an afternoon. Tested harder than it was built. Documented because the code isn't enough.*

> *engram (noun): a hypothesized physical trace of memory stored in the brain — the biological basis of how memories persist.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)](#)
[![Protocol](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://modelcontextprotocol.io)
[![CI](https://github.com/lalithbuilds/engram-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/lalithbuilds/engram-mcp/actions/workflows/ci.yml)

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
*   **Zero Infrastructure:** No databases to spin up. Engram automatically creates a local SQLite file in your home directory (`~/engram-mcp/memory.db`).
*   **Zero API Costs:** Because it uses local BM25/FTS5 keyword indexing instead of semantic embeddings, you pay $0 in API credits for memory retrieval.
*   **Total Data Privacy:** Your codebase context and architectural secrets never leave your local machine.

---

## Why This Exists (Vs The Ecosystem)

The AI agent memory ecosystem (like **Letta/MemGPT** or **AgentMemory**) is currently dominated by heavy frameworks requiring Postgres, pgvector, 15+ dependencies, and cloud embedding models. 

**Engram is the "Occam's Razor" alternative.** It rejects semantic vector embeddings in favor of blazing-fast SQLite FTS5 (BM25 keyword search). 
* You don't need a 768-dimensional vector embedding to remember that you prefer `pnpm` over `npm`. 
* You don't need an external API call to recall your project's architecture. 

Engram is for developers who want **100% local, zero-dependency, zero-bloat** agent memory that works completely offline and runs in <2ms.

## 🚀 Core Capabilities & Features

1.  **🐍 Zero Dependencies**
    Runs entirely on the Python Standard Library (`sqlite3`, `json`, `sys`, `hashlib`, `curses`). No `pip install` required.
2.  **⏳ Intelligent Auto-Decay (Forgetting Mechanism)**
    Unlike other servers that hoard data forever, Engram prevents stale context poisoning by employing a background auto-decay algorithm:
    *   Whenever an agent searches or retrieves a memory, it automatically bumps the `access_count` to signal importance.
    *   Whenever the MCP server spins up, it runs a background decay query: any memory that hasn't been accessed in 30 days automatically loses 1 point of `importance`.
    Your agent's context window stays clean, relevant, and self-maintaining without manual intervention.
3.  **🛡️ Enterprise-Grade Concurrency & Backups**
    Designed for multi-agent workflows. Engram implements SQLite Write-Ahead Logging (`PRAGMA journal_mode=WAL`) and strict connection timeouts. You can run Cursor and Claude Code simultaneously without triggering `database is locked` crashes. The system also performs daily automatic native SQLite backups (`memory.db.bak`) to protect against payload corruption.
4.  **🔒 Payload Bounding & Resilience**
    Engram strictly clamps memory outputs (max 8 results) to prevent LLM context-window blowouts, and truncates incoming memories to 8,000 characters to prevent payload bloat.
5.  **🧠 Conflict Surfacing (Self-Healing)**
    Built-in heuristic checks warn AI agents during memory saving if they are attempting to store contradicting contexts (e.g. "We use Postgres" vs "We use Mongo").
6.  **⌨️ Advanced CLI & Terminal UI (TUI)**
    Comes with a built-in terminal tool (`engram.py`) and a full-screen interactive `tui` dashboard. Human developers can manually view, edit, export, import, or search the agent's memories at any time, with deterministic `--json` outputs available for machine parsing.

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

# Search what the agent knows about a topic (can also output as JSON)
python3 engram.py --json search "Tailwind"

# List all memories in the database
python3 engram.py list

# Open the interactive Terminal UI Dashboard
python3 engram.py tui

# Delete a specific memory by its ID
python3 engram.py delete abc123def456

# View database size and category breakdown
python3 engram.py stats

# Export memories to a JSON file (or import them) for Git sync
python3 engram.py export backup.json
python3 engram.py import backup.json
```

---

## 🤝 Contributing

We welcome contributions! Specifically, we are looking for help improving the terminal UI (TUI) and making FTS5 search even smarter.
Check out our issues labeled `good first issue` to get started. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT — See [LICENSE](LICENSE) for details. Built by [Lalith Chandra](https://github.com/lalithbuilds).

---
*If Engram saves you from repeating yourself to an AI, consider giving it a ⭐!*