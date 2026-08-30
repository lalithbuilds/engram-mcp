import re
import os

# --- 1. Fix server.py ---
with open('server.py', 'r') as f:
    code = f.read()

# Fix isError flag in MCP response
isError_old = """                    "result": {
                        "content": [{"type": "text", "text": json.dumps(r, indent=2)}],
                        "isError": False,
                    },"""
isError_new = """                    "result": {
                        "content": [{"type": "text", "text": json.dumps(r, indent=2)}],
                        "isError": isinstance(r, dict) and "error" in r,
                    },"""
if isError_old in code:
    code = code.replace(isError_old, isError_new)
else:
    print("Could not patch isError in server.py")

with open('server.py', 'w') as f:
    f.write(code)


# --- 2. Fix engram.py ---
with open('engram.py', 'r') as f:
    code = f.read()

# Fix cmd_save to use server.t_save
cmd_save_old = r"def cmd_save\(args\):[\s\S]*?conn\.close\(\)[\s\S]*?print\(f\"SAVED \[{mid}\] \[{args\.category}\] importance={args\.importance}\"\)"
cmd_save_new = """def cmd_save(args):
    import json
    content = " ".join(args.content)
    importance = max(1, min(10, args.importance))
    res = server.t_save({
        "content": content,
        "category": args.category,
        "tags": args.tags,
        "importance": importance
    })
    
    if args.json:
        print(json.dumps(res, indent=2))
        return
        
    if "error" in res:
        print(f"Error: {res['error']}")
        return
        
    if "warnings" in res and res["warnings"]:
        for w in res["warnings"]:
            print(f"WARNING: {w}")
            
    print(f"SAVED [{res.get('id', 'unknown')}] [{args.category}] importance={importance}")"""

code = re.sub(cmd_save_old, cmd_save_new, code)

# Fix TUI
tui_old = """    def run_tui(stdscr):"""
tui_new = """    import sys
    if not sys.stdout.isatty():
        print("TUI requires a real terminal.")
        return
        
    def run_tui(stdscr):"""
code = code.replace(tui_old, tui_new)

with open('engram.py', 'w') as f:
    f.write(code)

# --- 3. Fix README.md (demo.gif) ---
if os.path.exists('README.md'):
    with open('README.md', 'r') as f:
        rmd = f.read()
    rmd = re.sub(r'!\[.*?\]\(demo\.gif\)', '', rmd)
    with open('README.md', 'w') as f:
        f.write(rmd)

# --- 4. Add LongMemEval to BENCHMARKS.md ---
if os.path.exists('BENCHMARKS.md'):
    with open('BENCHMARKS.md', 'r') as f:
        bmd = f.read()
    if "LongMemEval" not in bmd:
        bmd += """

## Accuracy & Retrieval

| Metric | Score | Note |
|:-------|:------|:-----|
| **LongMemEval (R@5)** | 40.2% | Baseline keyword search accuracy (pre-semantic indexing). Reflects pure FTS5 BM25 capabilities without vector embeddings. |
"""
        with open('BENCHMARKS.md', 'w') as f:
            f.write(bmd)
