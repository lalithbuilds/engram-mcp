import ast
import os

def check_sql_injection(filepath):
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    flaws = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in ('execute', 'executemany'):
                # Check if the first argument (query) is an f-string or formatted string
                if node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.JoinedStr):
                        flaws.append(f"Line {node.lineno}: Potential SQL Injection via f-string in execute().")
                    elif isinstance(first_arg, ast.Call) and isinstance(first_arg.func, ast.Attribute) and first_arg.func.attr == 'format':
                        flaws.append(f"Line {node.lineno}: Potential SQL Injection via .format() in execute().")
    return flaws

print("--- SQL INJECTION AUDIT ---")
for f in ["server.py", "engram.py"]:
    print(f"Checking {f}...")
    res = check_sql_injection(f)
    for r in res:
        print(f"  {r}")
    if not res:
        print("  Clean.")

print("\n--- RESOURCE LEAK AUDIT (Missing conn.close) ---")
# engram.py uses short-lived connections. We should ensure they close.
with open("engram.py", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "get_db()" in line and "server." not in line: # engram's get_db
            # just a heuristic
            pass

