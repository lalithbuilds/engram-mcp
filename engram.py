#!/usr/bin/env python3
"""
engram — CLI wrapper for the Engram local memory DB
Usage:
  engram save "your memory text" --category project --tags "tag1,tag2" --importance 8
  engram search "query"
  engram recall
  engram list
  engram stats
  engram delete <id>
"""

import sys
import json
import sqlite3
import hashlib
import datetime
import argparse
from pathlib import Path
import os
import server

def get_db():
    # Reuse server's get_db to handle schema initialization properly
    return server.get_db()


def now():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat()


def make_id(content):
    return hashlib.sha1(f"{content}".encode()).hexdigest()[:12]


def cmd_save(args):
    content    = " ".join(args.content)
    category   = args.category or "general"
    tags       = args.tags or ""
    importance = args.importance or 5
    mid = make_id(content)
    conn = get_db()
    conn.execute(
        """INSERT INTO memories (id,category,content,tags,importance,created_at,updated_at,access_count,last_accessed_at) 
           VALUES(?,?,?,?,?,?,?,0,?) 
           ON CONFLICT(id) DO UPDATE SET 
           category=excluded.category, tags=excluded.tags, importance=excluded.importance, updated_at=excluded.updated_at, last_accessed_at=excluded.last_accessed_at""",
        (mid, category, content, tags, importance, now(), now(), now())
    )
    conn.execute("DELETE FROM memories_fts WHERE id=?", (mid,))
    conn.execute("INSERT INTO memories_fts (id, content) VALUES (?, ?)", (mid, content))
    conn.commit()
    conn.close()
    print(f"SAVED  id={mid}  cat={category}  importance={importance}")


def cmd_search(args):
    query = " ".join(args.query)
    limit = args.limit or 5
    conn = get_db()
    if not query.isascii():
        rows = conn.execute(
            "SELECT id,category,content,tags,importance,created_at FROM memories WHERE content LIKE ? LIMIT ?",
            (f"%{query}%", limit)
        ).fetchall()
    else:
        try:
            rows = conn.execute("""
                SELECT m.id, m.category, m.content, m.tags, m.importance, m.created_at
                FROM memories_fts f JOIN memories m ON f.id=m.id
                WHERE memories_fts MATCH ? ORDER BY rank LIMIT ?
            """, (query, limit)).fetchall()
        except:
            rows = conn.execute(
                "SELECT id,category,content,tags,importance,created_at FROM memories WHERE content LIKE ? LIMIT ?",
                (f"%{query}%", limit)
            ).fetchall()
        
    if rows:
        ids = [r['id'] for r in rows]
        placeholders = ",".join(["?"] * len(ids))
        conn.execute(f"UPDATE memories SET access_count = access_count + 1, updated_at = ?, last_accessed_at = ? WHERE id IN ({placeholders})", [now(), now()] + ids)
        conn.commit()
        
    conn.close()
    if not rows:
        print("No results.")
        return
    for r in rows:
        print(f"\n[{r['id']}] [{r['category']}] importance={r['importance']}")
        print(f"  {r['content'][:200]}")
        print(f"  tags: {r['tags']}  created: {r['created_at'][:10]}")


def cmd_recall(args):
    limit = args.limit or 3
    min_imp = args.min_importance or 7
    conn = get_db()
    rows = conn.execute(
        "SELECT id,category,content,tags,importance FROM memories WHERE importance>=? ORDER BY importance DESC LIMIT ?",
        (min_imp, limit)
    ).fetchall()
    
    if rows:
        ids = [r['id'] for r in rows]
        placeholders = ",".join(["?"] * len(ids))
        conn.execute(f"UPDATE memories SET access_count = access_count + 1, updated_at = ?, last_accessed_at = ? WHERE id IN ({placeholders})", [now(), now()] + ids)
        conn.commit()
        
    conn.close()
    if not rows:
        print("No high-importance memories.")
        return
    for r in rows:
        print(f"\n[{r['id']}] [{r['category']}] importance={r['importance']}")
        print(f"  {r['content'][:200]}")


def cmd_list(args):
    conn = get_db()
    rows = conn.execute(
        "SELECT id,category,content,importance,created_at FROM memories ORDER BY importance DESC,created_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    if not rows:
        print("Memory bank is empty.")
        return
    print(f"{'ID':<14} {'CAT':<12} {'IMP':<5} {'DATE':<12} CONTENT")
    print("-" * 80)
    for r in rows:
        preview = r["content"][:45].replace("\n"," ")
        print(f"{r['id']:<14} {r['category']:<12} {r['importance']:<5} {r['created_at'][:10]:<12} {preview}")


def cmd_stats(args):
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    cats  = conn.execute("SELECT category, COUNT(*) as c FROM memories GROUP BY category ORDER BY c DESC").fetchall()
    conn.close()
    size = server.DB_PATH.stat().st_size
    print(f"TOTAL MEMORIES : {total}")
    print(f"DB SIZE        : {size:,} bytes  ({size//1024} KB)")
    print(f"DB PATH        : {server.DB_PATH}")
    print(f"\nCATEGORIES:")
    for r in cats:
        print(f"  {r['category']:<20} {r['c']} memories")


def cmd_delete(args):
    conn = get_db()
    conn.execute("DELETE FROM memories WHERE id=?", (args.id,))
    conn.execute("DELETE FROM memories_fts WHERE id=?", (args.id,))
    conn.commit()
    conn.close()
    print(f"DELETED {args.id}")


def main():
    parser = argparse.ArgumentParser(description="engram — Engram local memory CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_save = sub.add_parser("save", help="Save a memory")
    p_save.add_argument("content", nargs="+")
    p_save.add_argument("--category", "-c", default="general")
    p_save.add_argument("--tags", "-t", default="")
    p_save.add_argument("--importance", "-i", type=int, default=5)

    p_search = sub.add_parser("search", help="Search memories")
    p_search.add_argument("query", nargs="+")
    p_search.add_argument("--limit", "-l", type=int, default=5)

    p_recall = sub.add_parser("recall", help="Recall top memories (session start)")
    p_recall.add_argument("--limit", "-l", type=int, default=3)
    p_recall.add_argument("--min-importance", dest="min_importance", type=int, default=7)

    sub.add_parser("list", help="List all memories")
    sub.add_parser("stats", help="DB stats")

    p_del = sub.add_parser("delete", help="Delete a memory by ID")
    p_del.add_argument("id")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return

    cmds = {
        "save": cmd_save,
        "search": cmd_search,
        "recall": cmd_recall,
        "list": cmd_list,
        "stats": cmd_stats,
        "delete": cmd_delete,
    }
    cmds[args.cmd](args)


if __name__ == "__main__":
    main()
