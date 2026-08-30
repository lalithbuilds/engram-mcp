import re

with open("server.py", "r") as f:
    code = f.read()

# Fix ghost deletes in server.py
delete_old = """    conn = get_db()
    conn.execute("DELETE FROM memories WHERE id=?", (m,))
    conn.execute("DELETE FROM memories_fts WHERE id=?", (m,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": m}"""
    
delete_new = """    conn = get_db()
    cursor = conn.execute("DELETE FROM memories WHERE id=?", (m,))
    if cursor.rowcount == 0:
        conn.close()
        return {"error": "memory not found"}
    conn.execute("DELETE FROM memories_fts WHERE id=?", (m,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": m}"""
code = code.replace(delete_old, delete_new)

with open("server.py", "w") as f:
    f.write(code)

with open("engram.py", "r") as f:
    code = f.read()

# Fix ghost deletes in engram.py
cmd_delete_old = """def cmd_delete(args):
    conn = get_db()
    conn.execute("DELETE FROM memories WHERE id=?", (args.id,))
    conn.execute("DELETE FROM memories_fts WHERE id=?", (args.id,))
    conn.commit()
    conn.close()
    print(f"DELETED {args.id}")"""

cmd_delete_new = """def cmd_delete(args):
    import sys
    conn = get_db()
    cursor = conn.execute("DELETE FROM memories WHERE id=?", (args.id,))
    if cursor.rowcount == 0:
        conn.close()
        print(f"Error: memory {args.id} not found")
        sys.exit(1)
    conn.execute("DELETE FROM memories_fts WHERE id=?", (args.id,))
    conn.commit()
    conn.close()
    print(f"DELETED {args.id}")"""
code = code.replace(cmd_delete_old, cmd_delete_new)

# Fix exit codes for other commands
code = code.replace('print(f"Error: {res[\'error\']}")\n        return', 'print(f"Error: {res[\'error\']}")\n        import sys\n        sys.exit(1)')
code = code.replace('print(f"Failed to export: {e}")', 'print(f"Failed to export: {e}")\n        import sys\n        sys.exit(1)')
code = code.replace('print(f"Failed to load file: {e}")\n        return', 'print(f"Failed to load file: {e}")\n        import sys\n        sys.exit(1)')
code = code.replace('print("Invalid format: expected a JSON array of memories.")\n        return', 'print("Invalid format: expected a JSON array of memories.")\n        import sys\n        sys.exit(1)')

with open("engram.py", "w") as f:
    f.write(code)
