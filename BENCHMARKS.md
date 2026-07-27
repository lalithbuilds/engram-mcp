# 📊 Engram MCP Benchmarks

> Last updated: 2026-07-27 | Next run: Every Monday 09:00 UTC

## Performance Benchmarks (Speed)

### Latency
| Operation | Count | Total | Per-op |
|:----------|------:|------:|-------:|
| Save (FTS5 insert) | 1,000 | 6.6ms | 0.007ms |
| Search (FTS5 MATCH) | 100 | 2.1ms | 0.021ms |

### Retrieval Accuracy (LongMemEval)
| Metric | Score | Notes |
|--------|-------|-------|
| **Recall@5** | 40.20% | Keyword-only (no embeddings) |
| **Accuracy** | 40.20% | 500 LongMemEval questions |
| **Answerable** | 500/500 | Correctly handles unanswerable |

### FTS5 vs LIKE Performance
| Benchmark | Time | Ratio |
|-----------|------|-------|
| FTS5 (1000 queries) | 14.1ms | ✅ **Faster** |
| LIKE (1000 queries) | 92.9ms | Fallback |
| Speedup | **6.59x** | FTS5 wins |

### Concurrent Read Throughput (WAL Mode)
| Metric | Value |
|--------|-------|
| Threads | 5 |
| Reads per thread | 100 |
| Total reads | 500 |
| Time | 0.027s |
| **Throughput** | **18,508 reads/sec** |

---

## 🎯 What These Benchmarks Mean

### Speed
- **0.007ms save latency** = negligible (no perceptible delay in agent workflows)
- **0.021ms search latency** = faster than any network round-trip (Pinecone, API)
- **18,508 reads/sec** = easily handles multiple concurrent agents

### Accuracy
- **40.20% R@5 (keyword-only)** = This is the true baseline for non-semantic search! 
- Uses **FTS5 BM25 ranking** (no embeddings needed). Excellent for factual extraction and preferences.

### Cost
- **$0 per operation** (local SQLite, zero API calls)
- **Zero embedding costs** (no OpenAI/Cohere/external services)
- **Zero infrastructure** (single file, no database)

---

## 📈 Comparison: Engram vs. Alternatives

| System | R@5 | Latency | Cost | Deps |
|--------|-----|---------|------|------|
| **Engram** | 40.2% | 0.021ms | $0 | 0 |
| AgentMemory | 95.2% | ~5ms | $$ | 15+ |
| Letta | 88% | ~10ms | $$$ | 25+ |

**Tradeoff:** Engram sacrifices semantic accuracy for **zero dependencies, zero cost, offline-first**. It is perfect for tracking developer preferences (e.g. `pnpm` vs `npm`), code architectures, and standard project documentation without network round-trips.

---

## 🧪 How We Test

### LongMemEval (Functional Accuracy)
- **Dataset:** 500 multi-session QA pairs (`longmemeval_s_cleaned.json`)
- **Method:** Ingest history → retrieve relevant facts → answer question
- **Metric:** % of correct answers in top-5 results (R@5)

### Performance (Speed & Throughput)
- **FTS5 MATCH:** 1,000 queries, measure latency
- **Concurrent Reads:** 5 threads × 100 reads, WAL mode throughput
- **Hardware:** Standard CPU

---

## ⚡ Running Benchmarks Locally

```bash
# Clone the repository
git clone https://github.com/lalithbuilds/engram-mcp.git
cd engram-mcp

# Download LongMemEval dataset
mkdir -p benchmark/data
curl -L -o benchmark/data/longmemeval_s_cleaned.json https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json

# Run LongMemEval benchmark
python3 benchmark/benchmark_longmemeval.py

# Run custom benchmarks (FTS5 vs LIKE, auto-decay, concurrency)
python3 benchmark/benchmark_custom.py
```