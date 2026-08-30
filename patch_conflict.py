with open('server.py', 'r') as f:
    code = f.read()

import re

old_logic = """            query_str = " AND ".join(words[:5]) if len(words) > 2 else " OR ".join(words[:10])
            try:
                candidates = conn.execute(
                    \"\"\"
                    SELECT m.id, m.content
                    FROM memories_fts f JOIN memories m ON f.id=m.id
                    WHERE memories_fts MATCH ?
                    LIMIT 3
                    \"\"\",
                    (query_str,)
                ).fetchall()
                for c in candidates:
                    if c["id"] != mid:
                        warnings.append(f"Similar memory found (ID {c['id']}): {c['content'][:50]}... Did you mean to update it?")"""

new_logic = """            query_str = " OR ".join(words[:10])
            try:
                candidates = conn.execute(
                    "SELECT m.id, m.content FROM memories_fts f JOIN memories m ON f.id=m.id WHERE memories_fts MATCH ? LIMIT 10",
                    (query_str,)
                ).fetchall()
                for c in candidates:
                    if c["id"] != mid:
                        # Prevent false positive from 1 shared word by checking actual overlap
                        shared = set(w.lower() for w in words) & set(w.lower() for w in c["content"].split() if len(w) > 3)
                        if len(shared) >= 2:
                            warnings.append(f"Similar memory found (ID {c['id']}): {c['content'][:50]}... Did you mean to update it?")"""

if old_logic in code:
    code = code.replace(old_logic, new_logic)
else:
    print("Could not find old logic block")
with open('server.py', 'w') as f:
    f.write(code)
