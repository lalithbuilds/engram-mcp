# Benchmarks

<img src="https://capsule-render.vercel.app/api?type=rect&color=ff79c6&height=2&width=100%"/>


> Last updated: 2026-08-30 (Corrected by Audit)

## Performance on `ubuntu-latest` / Python 3.12

| Operation | Count | Total | Per-op |
|:----------|------:|------:|-------:|
| Save (memory_save real load) | 1,000 | 800ms | 0.800ms |
| Search (10k rows FTS5) | 100 | ~700ms | 7.000ms |
| Parallel Writes (WAL)| 50 | ~11.0ms | 0.220ms |

*Metrics have been updated to reflect real-world payload handling (including conflict detection heuristics and FTS5 synchronization) rather than raw batch inserts.*


## Accuracy & Retrieval

| Metric | Score | Note |
|:-------|:------|:-----|
| **LongMemEval (R@5)** | 40.2% | Baseline keyword search accuracy (pre-semantic indexing). Reflects pure FTS5 BM25 capabilities without vector embeddings. |
