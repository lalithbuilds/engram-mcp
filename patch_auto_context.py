import re

with open("server.py", "r") as f:
    code = f.read()

# Fix context injection
ctx_old = 'lines = [f"[{r[\'category\']}] {r[\'content\']}" for r in rows]'
ctx_new = 'lines = [f"<memory id=\\"{r[\'id\']}\\" category=\\"{r[\'category\']}\\">\\n{r[\'content\']}\\n</memory>" for r in rows]'
code = code.replace(ctx_old, ctx_new)

# Fix get_db side-effects
get_db_old = "def get_db():"
get_db_new = "def get_db(read_only=False):"
code = code.replace(get_db_old, get_db_new)

decay_old = "if time.time() - _LAST_DECAY_RUN > 3600:"
decay_new = "if not read_only and time.time() - _LAST_DECAY_RUN > 3600:"
code = code.replace(decay_old, decay_new)

with open("server.py", "w") as f:
    f.write(code)

