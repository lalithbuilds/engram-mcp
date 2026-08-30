import server
import json
import traceback

print("Checking JSON schema logic...")
try:
    schema = server.TOOLS
    for t_name, t_info in schema.items():
        assert "fn" in t_info
        assert "description" in t_info
        assert "inputSchema" in t_info
except Exception as e:
    traceback.print_exc()

print("Checking dependencies...")
import ast
with open('server.py') as f:
    node = ast.parse(f.read())
for n in ast.walk(node):
    if isinstance(n, ast.Import):
        for name in n.names:
            print(f"Import: {name.name}")
    elif isinstance(n, ast.ImportFrom):
        print(f"ImportFrom: {n.module}")
