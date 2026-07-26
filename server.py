#!/usr/bin/env python3
"""
ENGRAM MCP SERVER v4.1 — PONYTAIL EDITION (July 2026)
Zero bloat. Zero cloud. Pure SQLite Standard Library.
"""

import json, sys, sqlite3, hashlib
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path.home() / "engram-mcp" / "memory.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL DEFAULT 'general',
    content TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '',
    importance INTEGER NOT NULL DEFAULT 5,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    access_count INTEGER NOT NULL DEFAULT 0
);
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(id, content, tokenize='porter unicode61');
"""

_SCHEMA_INITIALIZED = False

def get_db():
    global _SCHEMA_INITIALIZED
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    if not _SCHEMA_INITIALIZED:
        conn.executescript(SCHEMA)
        _SCHEMA_INITIALIZED = True
    return conn

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()

def make_id(content):
    return hashlib.sha1(f"{content}{now()}".encode()).hexdigest()[:12]

def safe_int(val, default, lo=None, hi=None):
    try:
        v = int(val)
    except (ValueError, TypeError):
        v = default
    if lo is not None: v = max(lo, v)
    if hi is not None: v = min(hi, v)
    return v

MAX_CONTENT = 8000

# ── TOOL FUNCTIONS ──────────────────────────────────────────────────────────

def t_auto_context(a):
    limit = safe_int(a.get("limit", 5), 5, 1, 8)
    min_imp = safe_int(a.get("min_importance", 7), 7, 1, 10)
    conn = get_db()
    rows = conn.execute(
        "SELECT id, category, content, importance FROM memories WHERE importance >= ? ORDER BY importance DESC, created_at DESC LIMIT ?",
        (min_imp, limit)
    ).fetchall()
    conn.close()

    lines = [f"[{r['category']}] {r['content']}" for r in rows]
    cats = {}
    for r in rows:
        cats[r['category']] = cats.get(r['category'], 0) + 1

    return {"ctx": "\n".join(lines), "n": len(lines), "cats": cats}

def t_smart_search(a):
    query = a.get("query", "").strip()
    limit = safe_int(a.get("limit", 5), 5, 1, 8)
    if not query: return {"error": "query required"}

    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT m.id, m.category, m.content, m.tags, m.importance, m.created_at
            FROM memories_fts f JOIN memories m ON f.id=m.id
            WHERE memories_fts MATCH ? ORDER BY rank, m.importance DESC LIMIT ?
        """, (query, limit)).fetchall()
    except Exception:
        rows = conn.execute(
            "SELECT id, category, content, tags, importance, created_at FROM memories WHERE content LIKE ? LIMIT ?",
            (f"%{query}%", limit)
        ).fetchall()
    conn.close()

    results = [{"id": r["id"], "category": r["category"], "content": r["content"], "importance": r["importance"]} for r in rows]
    return {"results": results, "n": len(results)}

def t_save(a):
    content = a.get("content", "").strip()
    if not content: return {"error": "content required"}
    content = content[:MAX_CONTENT]
    cat = a.get("category", "general")
    tags = a.get("tags", "")
    imp = safe_int(a.get("importance", 5), 5, 1, 10)
    mid = make_id(content)

    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO memories (id,category,content,tags,importance,created_at,updated_at,access_count) VALUES(?,?,?,?,?,?,?,0)",
        (mid, cat, content, tags, imp, now(), now())
    )
    conn.execute("INSERT OR REPLACE INTO memories_fts (id, content) VALUES (?, ?)", (mid, content))
    conn.commit()
    conn.close()
    return {"id": mid, "status": "saved", "cat": cat, "imp": imp}

def t_extract_save(a):
    text = a.get("text", "").strip()
    cat = a.get("category", "general")
    if not text: return {"error": "text required"}
    imp = safe_int(a.get("base_importance", 6), 6, 1, 10)

    mid = make_id(text)
    conn = get_db()
    content = text[:MAX_CONTENT]
    conn.execute(
        "INSERT OR REPLACE INTO memories (id,category,content,tags,importance,created_at,updated_at,access_count) VALUES(?,?,?,?,?,?,?,0)",
        (mid, cat, content, "", imp, now(), now())
    )
    conn.execute("INSERT OR REPLACE INTO memories_fts (id, content) VALUES (?, ?)", (mid, content))
    conn.commit()
    conn.close()
    return {"saved": [{"id": mid, "preview": text[:50]}], "saved_n": 1, "skipped": 0}

def t_delete(a):
    m = a.get("id", "").strip()
    if not m: return {"error": "id required"}

    conn = get_db()
    conn.execute("DELETE FROM memories WHERE id=?", (m,))
    conn.execute("DELETE FROM memories_fts WHERE id=?", (m,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": m}

def t_stats(a):
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    cats = {row['category']: row['c'] for row in conn.execute("SELECT category, COUNT(*) as c FROM memories GROUP BY category").fetchall()}
    conn.close()
    size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
    return {"memories": total, "categories": len(cats), "db_bytes": size, "details": cats}

# ── REGISTRY ────────────────────────────────────────────────────────────────

TOOLS = {
    "memory_auto_context": {
        "fn": t_auto_context,
        "description": "Session boot: returns top memories + category map. Call ONCE at session start. Hard cap 8 results.",
        "inputSchema": {"type":"object","properties":{
            "topic":{"type":"string","description":"Current task topic (optional)"},
            "limit":{"type":"integer","description":"Max results 1-8, default 5"},
            "min_importance":{"type":"integer","description":"Min importance 1-10, default 7"}}}
    },
    "memory_smart_search": {
        "fn": t_smart_search,
        "description": "Keyword search: FTS5 full-text search with LIKE fallback. Use mid-session for topic context.",
        "inputSchema": {"type":"object","properties":{
            "query":{"type":"string","description":"Search query"},
            "limit":{"type":"integer","description":"Max 1-8, default 5"}},
            "required":["query"]}
    },
    "memory_save": {
        "fn": t_save,
        "description": "Save one memory with category, tags, importance (1-10). Auto-deduplication. Max 8000 chars.",
        "inputSchema": {"type":"object","properties":{
            "content":{"type":"string"},
            "category":{"type":"string","description":"project|preference|workflow|decision|fact|person|general"},
            "tags":{"type":"string"},
            "importance":{"type":"integer"}},
            "required":["content"]}
    },
    "memory_extract_save": {
        "fn": t_extract_save,
        "description": "Extract+save facts from text block. Use at session end. Max 8000 chars.",
        "inputSchema": {"type":"object","properties":{
            "text":{"type":"string","description":"Text to extract facts from"},
            "category":{"type":"string"},
            "base_importance":{"type":"integer","description":"Base importance 1-10, default 6"}},
            "required":["text"]}
    },
    "memory_delete": {
        "fn": t_delete,
        "description": "Delete memory by id. Also removes from FTS index.",
        "inputSchema": {"type":"object","properties":{"id":{"type":"string"}},"required":["id"]}
    },
    "memory_stats": {
        "fn": t_stats,
        "description": "DB stats: memory count, categories, size. No content returned.",
        "inputSchema": {"type":"object","properties":{}}
    }
}

# ── JSON-RPC 2.0 STDIO ──────────────────────────────────────────────────────

def send(o): sys.stdout.write(json.dumps(o)+"\n"); sys.stdout.flush()

def handle(msg):
    method=msg.get("method",""); mid_=msg.get("id")
    if method=="initialize":
        send({"jsonrpc":"2.0","id":mid_,"result":{
            "protocolVersion":"2024-11-05","capabilities":{"tools":{}},
            "serverInfo":{"name":"engram-mcp","version":"4.1.0"}}})
    elif method=="tools/list":
        send({"jsonrpc":"2.0","id":mid_,"result":{"tools":[
            {"name":n,"description":m["description"],"inputSchema":m["inputSchema"]}
            for n,m in TOOLS.items()]}})
    elif method=="tools/call":
        p=msg.get("params",{}); tn=p.get("name",""); ta=p.get("arguments",{})
        if tn not in TOOLS:
            send({"jsonrpc":"2.0","id":mid_,"error":{"code":-32601,"message":f"Unknown: {tn}"}}); return
        try:
            r=TOOLS[tn]["fn"](ta)
            send({"jsonrpc":"2.0","id":mid_,"result":{"content":[{"type":"text","text":json.dumps(r,indent=2)}],"isError":False}})
        except Exception as e:
            send({"jsonrpc":"2.0","id":mid_,"result":{"content":[{"type":"text","text":f"ERR:{e}"}],"isError":True}})
            return {"jsonrpc":"2.0","id":mid_,"result":{"content":[{"type":"text","text":f"ERR:{e}"}],"isError":True}}
    elif method in ("notifications/initialized","notifications/cancelled"): return None
    elif mid_ is not None:
        return {"jsonrpc":"2.0","id":mid_,"error":{"code":-32601,"message":f"Unknown method:{method}"}}

def main():
    sys.stderr.write(f"[engram-mcp v4.1] Booting...\n")
    if len(sys.argv) > 1:
        if sys.argv[1] == "--diagnostics": sys.exit(0)
    init_db()
    
    for line in sys.stdin:
        try:
            req = json.loads(line)
            if "method" in req:
                res = handle(req)
                if res: sys.stdout.write(json.dumps(res) + "\n"); sys.stdout.flush()
        except Exception as e: sys.stderr.write(f"[engram-mcp] {e}\n")

if __name__=="__main__": main()
