with open("engram.py", "r") as f:
    code = f.read()

# Make read-only CLI commands not trigger decay/backup
code = code.replace("def cmd_search(args):\n    conn = get_db()", "def cmd_search(args):\n    conn = server.get_db(read_only=True)")
code = code.replace("def cmd_list(args):\n    conn = get_db()", "def cmd_list(args):\n    conn = server.get_db(read_only=True)")
code = code.replace("def cmd_stats(args):\n    conn = get_db()", "def cmd_stats(args):\n    conn = server.get_db(read_only=True)")
code = code.replace("def cmd_export(args):\n    conn = server.get_db()", "def cmd_export(args):\n    conn = server.get_db(read_only=True)")
code = code.replace("def run_tui(stdscr):\n        conn = server.get_db()", "def run_tui(stdscr):\n        conn = server.get_db(read_only=True)")

with open("engram.py", "w") as f:
    f.write(code)
