import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE VIRTUAL TABLE t USING fts5(content)")
conn.execute("INSERT INTO t VALUES ('Apple')")

try:
    print(conn.execute("SELECT * FROM t WHERE t MATCH ?", ("Apple",)).fetchall())
    print(conn.execute("SELECT * FROM t WHERE t MATCH ?", ("",)).fetchall())
except Exception as e:
    print("Error:", e)
