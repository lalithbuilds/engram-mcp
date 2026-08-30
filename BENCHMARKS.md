# Benchmarks

> Last updated: 2026-08-30 (Corrected by Audit)

## Performance on `ubuntu-latest` / Python 3.12

| Operation | Count | Total | Per-op |
|:----------|------:|------:|-------:|
| Save (memory_save real load) | 1,000 | 800ms | 0.800ms |
| Search (10k rows FTS5) | 100 | ~700ms | 7.000ms |
| Parallel Writes (WAL)| 50 | ~11.0ms | 0.220ms |

*Metrics have been updated to reflect real-world payload handling (including conflict detection heuristics and FTS5 synchronization) rather than raw batch inserts.*
