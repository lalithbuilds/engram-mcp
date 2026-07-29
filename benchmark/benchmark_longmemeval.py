#!/usr/bin/env python3
"""
LongMemEval Benchmark for Engram MCP
Measures retrieval accuracy (R@5, R@10, etc.)
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import Engram's core functions
sys.path.insert(0, str(Path(__file__).parent.parent))

# Need to set DB_PATH before importing server so it creates isolated benchmark DB
db_path = Path.home() / "engram-benchmarks" / "memory.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
os.environ["ENGRAM_DB_PATH"] = str(db_path)

import server  # Engram's server module


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()


def load_longmemeval(dataset_path):
    with open(dataset_path, "r") as f:
        return json.load(f)


def ingest_memory(conn, item):
    sessions = item.get("haystack_sessions", [])

    for session in sessions:
        for turn in session:
            content = turn.get("content", "")
            if not content:
                continue

            mid = server.make_id(content)
            conn.execute(
                """INSERT INTO memories (id, category, content, tags, importance, created_at, updated_at, access_count, last_accessed_at)
                   VALUES(?, ?, ?, ?, ?, ?, ?, 0, ?)
                   ON CONFLICT(id) DO UPDATE SET
                   category=excluded.category, importance=excluded.importance, updated_at=excluded.updated_at, last_accessed_at=excluded.last_accessed_at""",
                (mid, "history", content, "longmemeval", 7, now(), now(), now()),
            )

            # Sync FTS index
            conn.execute("DELETE FROM memories_fts WHERE id=?", (mid,))
            conn.execute(
                "INSERT INTO memories_fts (id, content) VALUES (?, ?)", (mid, content)
            )

    conn.commit()


def search_memory(conn, query, limit=5):
    if not query.isascii():
        rows = conn.execute(
            "SELECT id, category, content, importance FROM memories WHERE content LIKE ? LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
    else:
        try:
            # Extract alphanumeric words to avoid FTS5 syntax errors with punctuation
            import re

            words = [w for w in re.findall(r"\w+", query) if len(w) > 2]
            fts_query = " OR ".join(words) if words else query

            rows = conn.execute(
                """
                SELECT m.id, m.category, m.content, m.importance
                FROM memories_fts f JOIN memories m ON f.id=m.id
                WHERE memories_fts MATCH ? ORDER BY rank LIMIT ?
            """,
                (fts_query, limit),
            ).fetchall()
        except Exception as e:
            print(f"Exception in FTS: {e}")
            rows = conn.execute(
                "SELECT id, category, content, importance FROM memories WHERE content LIKE ? LIMIT ?",
                (f"%{query}%", limit),
            ).fetchall()

    return [{"id": r["id"], "content": r["content"]} for r in rows]


def evaluate_single_item(conn, item):
    question = item.get("question", "")
    answer = item.get("answer", "")
    is_unanswerable = item.get("is_unanswerable", False)

    if not question:
        return None, None

    results = search_memory(conn, question, limit=5)
    result_texts = [r["content"] for r in results]

    if is_unanswerable:
        return False, True

    import re

    # Check if answer text appears in retrieved results using precise word boundaries
    pattern = r"\b" + re.escape(str(answer).lower()) + r"\b"
    correct = any(re.search(pattern, str(text).lower()) for text in result_texts)
    return correct, False


def run_benchmark(dataset_path, output_file="longmemeval_results.json"):
    print(f"[engram-longmemeval] Loading dataset from {dataset_path}")
    dataset = load_longmemeval(dataset_path)

    results = {
        "timestamp": now(),
        "dataset": str(dataset_path),
        "total_items": len(dataset),
        "items": [],
    }

    correct_count = 0
    unanswerable_count = 0

    conn = server.get_db()

    for idx, item in enumerate(dataset):
        conn.execute("DELETE FROM memories")
        conn.execute("DELETE FROM memories_fts")
        conn.commit()

        print(f"[{idx + 1}/{len(dataset)}] Ingesting history...", end="\r")
        ingest_memory(conn, item)

        correct, is_unansw = evaluate_single_item(conn, item)

        if correct is not None:
            results["items"].append(
                {
                    "question": item.get("question", ""),
                    "is_unanswerable": is_unansw,
                    "correct": correct,
                }
            )

            if is_unansw:
                unanswerable_count += 1
            elif correct:
                correct_count += 1

    conn.close()

    answerable_items = [i for i in results["items"] if not i["is_unanswerable"]]
    answerable_correct = sum(1 for i in answerable_items if i["correct"])

    results["metrics"] = {
        "total_questions": len(results["items"]),
        "answerable_questions": len(answerable_items),
        "unanswerable_questions": unanswerable_count,
        "correct_answers": answerable_correct,
        "recall_at_5": round(answerable_correct / len(answerable_items), 4)
        if answerable_items
        else 0,
        "accuracy": round(answerable_correct / len(results["items"]), 4)
        if results["items"]
        else 0,
    }

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("LONGMEMEVAL BENCHMARK RESULTS FOR ENGRAM MCP")
    print("=" * 60)
    print(f"Total questions:       {results['metrics']['total_questions']}")
    print(f"Answerable questions:  {results['metrics']['answerable_questions']}")
    print(f"Unanswerable questions: {results['metrics']['unanswerable_questions']}")
    print(f"Correct answers:       {results['metrics']['correct_answers']}")
    print(f"\n🏆 RECALL@5 (R@5):     {results['metrics']['recall_at_5'] * 100:.2f}%")
    print(f"📊 Accuracy:           {results['metrics']['accuracy'] * 100:.2f}%")
    print("=" * 60)
    return results


if __name__ == "__main__":
    dataset_path = Path(__file__).parent / "data" / "longmemeval_s_cleaned.json"

    if not dataset_path.exists():
        print(f"❌ Dataset not found at {dataset_path}")
        sys.exit(1)

    run_benchmark(dataset_path)
