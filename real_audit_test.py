import os
import time
import sqlite3
import server

db_path = server.DB_PATH
# Init DB
conn = server.get_db()

print("\n--- EBBINGHAUS DECAY TEST ---")
import re
# Properly escaping regex for Python inside the script
query_clean = " OR ".join(w for w in re.sub(r"[^\w\s]", " ", "Apple").strip().split() if w)

scores = conn.execute("""
    SELECT m.id, 
           rank, 
           (rank * m.importance * EXP(-0.05 * (julianday('now') - julianday(COALESCE(NULLIF(m.last_accessed_at, ''), m.created_at))))) as final_score
    FROM memories_fts f JOIN memories m ON f.id=m.id 
    WHERE memories_fts MATCH ? 
    ORDER BY final_score ASC
""", (query_clean,)).fetchall()

for row in scores:
    print(f"ID: {row['id']:<10} | Raw FTS5 Rank: {row['rank']:.4f} | Ebbinghaus Final Score: {row['final_score']:.4f}")
print("(Note: SQLite FTS5 ranks are negative; more negative is better. Notice the 45-day old memory's score is driven toward 0, making it rank worse).")

print("\n--- IMPORT SPEED BENCHMARK (10,000 Rows) ---")
import engram
import json
dummy_data = [{"id": f"dummy_{i}", "content": f"Bulk memory {i}", "importance": 5} for i in range(10000)]
with open("dummy_import.json", "w") as f:
    json.dump(dummy_data, f)

start_time = time.time()
args = type("Args", (), {"file": "dummy_import.json", "json": False})()
import sys
old_stdout = sys.stdout
with open(os.devnull, 'w') as devnull:
    sys.stdout = devnull
    try:
        engram.cmd_import(args)
    finally:
        sys.stdout = old_stdout

elapsed = time.time() - start_time
print(f"Imported 10,000 rows in: {elapsed:.4f} seconds")
conn.close()
