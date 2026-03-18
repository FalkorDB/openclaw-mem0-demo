# Mem0 + FalkorDB — Graph-Structured Agent Memory Demo

Persistent, graph-structured memory for AI agents using [Mem0](https://github.com/mem0ai/mem0) and [FalkorDB](https://falkordb.com). Each user gets an isolated knowledge graph — no shared state, no filtering, just clean per-user graphs.

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Your App   │─────▶│    Mem0     │─────▶│  FalkorDB   │
│  (Python)   │      │  (Memory)   │      │  (Graphs)   │
└─────────────┘      └──────┬──────┘      └─────────────┘
                            │
                     ┌──────▼──────┐
                     │   OpenAI    │
                     │ (Embeddings │
                     │  + LLM)     │
                     └─────────────┘
```

**How it works:**
1. **Mem0** manages the memory lifecycle — adding, searching, updating, and deleting memories
2. **mem0-falkordb** patches FalkorDB into Mem0 as a graph store (no Mem0 source changes)
3. **FalkorDB** stores entity relationships as graphs — one graph per user (`mem0_alice`, `mem0_bob`)
4. **OpenAI** provides embeddings for semantic search and LLM for entity extraction

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (for FalkorDB)
- Python 3.10+
- OpenAI API key

## Quick Start

### 1. Start FalkorDB

```bash
docker compose up -d
```

Verify it's running:

```bash
docker compose ps
# or
redis-cli -h localhost -p 6379 ping
# → PONG
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure your API key

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 4. Run the demo

**Quick start** (minimal example):

```bash
python demo_basic.py
```

**Full demo** (all features):

```bash
python demo.py
```

## What the Demo Shows

### `demo_basic.py` — Minimal Quick Start

The simplest possible integration in ~30 lines:
- Register the FalkorDB plugin
- Configure Mem0 with FalkorDB as graph store
- Add memories and search them

### `demo.py` — Comprehensive Demo

Five scenarios that showcase the full capabilities:

| Scenario | What it demonstrates |
|----------|---------------------|
| **Add & Search** | Store facts, search with natural language queries |
| **Multi-User Isolation** | Each user gets their own FalkorDB graph — no data leaks |
| **Memory Updates** | Mem0 handles conflicting info automatically |
| **List Memories** | Inspect all stored memories for a user |
| **Cleanup** | Drop a user's entire graph with one call |

## Configuration Reference

### FalkorDB Connection

```python
config = {
    "graph_store": {
        "provider": "falkordb",
        "config": {
            "host": "localhost",       # FalkorDB host
            "port": 6379,              # FalkorDB port
            "database": "mem0",        # Graph name prefix
            "username": None,          # Optional auth
            "password": None,          # Optional auth
        },
    },
    "llm": {
        "provider": "openai",
        "config": {"model": "gpt-4o-mini"},
    },
}
```

Each user gets their own graph: `{database}_{user_id}` (e.g., `mem0_alice`).

### Using FalkorDB Cloud

Replace the connection config:

```python
"config": {
    "host": "your-instance.falkordb.cloud",
    "port": 6379,
    "username": "default",
    "password": "your-password",
    "database": "mem0",
}
```

Sign up at [app.falkordb.cloud](https://app.falkordb.cloud).

## Inspecting the Graph

Connect to FalkorDB and query the graph directly:

```bash
redis-cli -h localhost -p 6379

# List all graphs
GRAPH.LIST

# Query alice's memory graph
GRAPH.QUERY mem0_alice "MATCH (n) RETURN n LIMIT 10"

# See relationships
GRAPH.QUERY mem0_alice "MATCH (a)-[r]->(b) RETURN a.name, type(r), b.name"
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ConnectionError` to FalkorDB | Ensure `docker compose up -d` is running and port 6379 is free |
| `OPENAI_API_KEY` error | Copy `.env.example` to `.env` and add your key |
| Empty search results | Verify memories were added with `m.get_all(user_id="...")` |
| Import errors | Ensure you're in the venv: `source .venv/bin/activate` |
| `register()` not called | Must call `register()` **before** `Memory.from_config()` |

## Resources

- [mem0-falkordb on PyPI](https://pypi.org/project/mem0-falkordb/)
- [mem0-falkordb GitHub](https://github.com/FalkorDB/mem0-falkordb)
- [Mem0 Documentation](https://docs.mem0.ai)
- [FalkorDB Documentation](https://docs.falkordb.com)
- [FalkorDB Cloud](https://app.falkordb.cloud)

## License

MIT
