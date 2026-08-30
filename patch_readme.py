import re

with open("README.md", "r") as f:
    readme = f.read()

# Fix the decay claim
decay_old = "any memory that hasn't been accessed in 30 days automatically loses 1 point of importance."
decay_new = "any memory that hasn't been accessed or modified in 30 days automatically decays down towards the importance floor."
if decay_old in readme:
    readme = readme.replace(decay_old, decay_new)

# Fix the exponential decay claim
exp_old = "Ebbinghaus exponential decay"
exp_new = "Ebbinghaus decay curve (native SQLite EXP() function)"
if exp_old in readme:
    readme = readme.replace(exp_old, exp_new)

# Fix prompt injection warning
sync_old = "git-sync your memory bank"
sync_new = "sync your memory.db file across machines (WARNING: Memories are injected into the agent context, so only store trusted data. Do not commit memory.db to public repositories!)"
if sync_old in readme:
    readme = readme.replace(sync_old, sync_new)

with open("README.md", "w") as f:
    f.write(readme)
