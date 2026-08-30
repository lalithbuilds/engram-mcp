import re

with open('server.py', 'r') as f:
    code = f.read()

old_logic = """shared = set(w.lower() for w in words) & set(w.lower() for w in c["content"].split() if len(w) > 3)"""
new_logic = """shared = set(w.lower() for w in words) & set(w.lower() for w in re.sub(r"[^\\w\\s]", " ", c["content"]).split() if len(w) > 3)"""

if old_logic in code:
    code = code.replace(old_logic, new_logic)
else:
    print("Could not find old logic block")

with open('server.py', 'w') as f:
    f.write(code)
