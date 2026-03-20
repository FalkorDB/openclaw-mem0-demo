# OpenClaw + Mem0 + FalkorDB — Persistent Graph Memory for AI Agents

Give your [OpenClaw](https://github.com/openclaw/openclaw) assistant persistent, graph-structured memory using [Mem0](https://docs.mem0.ai) and [FalkorDB](https://falkordb.com). The agent remembers user preferences, facts, and relationships across sessions — automatically.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  OpenClaw   │────▶│  @mem0/openclaw  │────▶│  FalkorDB   │
│  (Agent)    │     │  -mem0 (Plugin)  │     │  (Graphs)   │
└─────────────┘     └────────┬─────────┘     └─────────────┘
                             │
                      ┌──────▼──────┐
                      │   OpenAI    │
                      │ (Embeddings │
                      │  + LLM)     │
                      └─────────────┘
```

**How the pieces fit together:**

| Component | Role |
|-----------|------|
| **OpenClaw** | Personal AI assistant — the agent runtime and chat interface |
| **@falkordb/openclaw-mem0** | OpenClaw plugin — auto-recall/capture + 5 memory tools, with FalkorDB graph support |
| **Mem0 Node.js SDK** | Memory management — extracts, stores, and retrieves facts |
| **@falkordb/mem0** | TypeScript library — FalkorDB as a graph store for Mem0 (bundled in the plugin) |
| **FalkorDB** | Graph database — stores entity relationships per user |
| **OpenAI** | Embeddings for semantic search + LLM for entity extraction |

**Memory flow:**
1. You chat with your OpenClaw agent on any channel (WhatsApp, Telegram, Slack, CLI, etc.)
2. **Auto-Capture**: After each response, the mem0 plugin extracts entities and relationships
3. **Auto-Recall**: Before each response, vector search + graph traversal inject relevant memories
4. **FalkorDB** stores entity relationships as isolated per-user graphs (`mem0_alice`, `mem0_bob`)

## Prerequisites

- [Node.js ≥ 22](https://nodejs.org/) (for OpenClaw)
- [Docker](https://docs.docker.com/get-docker/) (for FalkorDB)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (for Python verification scripts)
- OpenAI API key

## Quick Start

### 1. Start FalkorDB

```bash
docker compose up -d
```

Verify it's running:

```bash
redis-cli -h localhost -p 6379 ping
# → PONG
```

### 2. Set up environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Export it so OpenClaw can use it
export OPENAI_API_KEY="sk-..."
```

### 3. Install and configure OpenClaw

```bash
# Install OpenClaw globally
npm install -g openclaw@latest

# Install the FalkorDB-enabled Mem0 memory plugin
openclaw plugins install @falkordb/openclaw-mem0

# Copy the provided config (OSS mode — fully self-hosted, no Mem0 Cloud needed)
mkdir -p ~/.openclaw && cp openclaw.json ~/.openclaw/openclaw.json
```

### 4. Start the OpenClaw gateway

```bash
openclaw onboard --install-daemon
# Or run directly:
openclaw gateway --port 18789 --verbose
```

### 5. Chat with your memory-enabled agent

```bash
# Send a message — the agent will auto-capture facts
openclaw agent --local --session-id demo --message "I'm a software engineer who loves Rust and hiking"

# Later, the agent auto-recalls relevant memories
openclaw agent --local --session-id demo --message "Recommend me a weekend project"
# → Agent remembers you like Rust and hiking!

# Use the CLI to search memories directly
openclaw mem0 search "what languages does the user know"

# View memory stats
openclaw mem0 stats
```

## OpenClaw Configuration

This repo includes two ready-to-use configs:

### `openclaw.json` — OSS Mode (default, self-hosted)

Fully local — no Mem0 Cloud account needed. Uses OpenAI for embeddings/LLM and FalkorDB for graph storage via [`@falkordb/openclaw-mem0`](https://www.npmjs.com/package/@falkordb/openclaw-mem0).

Key config points:
- **`gateway.mode: "local"`** — required for local-only operation
- **`plugins.slots.memory: "openclaw-mem0"`** — tells OpenClaw to use the mem0 plugin instead of the default `memory-core`
- **`oss.graphStore`** — configures FalkorDB as the graph backend

```jsonc
{
  "gateway": { "mode": "local" },
  "plugins": {
    "slots": { "memory": "openclaw-mem0" },
    "entries": {
      "openclaw-mem0": {
        "enabled": true,
        "config": {
          "mode": "open-source",
          "userId": "alice",
          "autoRecall": true,
          "autoCapture": true,
          "oss": {
            "embedder": { "provider": "openai", "config": { "model": "text-embedding-3-small" } },
            "vectorStore": { "provider": "memory", "config": { "dimension": 1536 } },
            "graphStore": {
              "provider": "falkordb",
              "config": { "host": "localhost", "port": 6379, "graphName": "mem0" }
            },
            "llm": { "provider": "openai", "config": { "model": "gpt-4o-mini" } }
          }
        }
      }
    }
  }
}
```

### `openclaw.platform-mode.json` — Platform Mode (Mem0 Cloud)

Uses Mem0's managed cloud with `enableGraph: true` for built-in graph entity relationships.

```jsonc
{
  "plugins": {
    "entries": {
      "openclaw-mem0": {
        "enabled": true,
        "config": {
          "mode": "platform",
          "apiKey": "${MEM0_API_KEY}",
          "userId": "alice",
          "enableGraph": true       // entity graph for relationships
        }
      }
    }
  }
}
```

To use Platform Mode: set `MEM0_API_KEY` in `.env` and copy `openclaw.platform-mode.json` to `~/.openclaw/openclaw.json`:

```bash
mkdir -p ~/.openclaw && cp openclaw.platform-mode.json ~/.openclaw/openclaw.json
```

### Agent Memory Tools

The mem0 plugin gives your OpenClaw agent five tools it can use during conversations:

| Tool | Description |
|------|-------------|
| `memory_search` | Search memories by natural language |
| `memory_store` | Explicitly save a fact (long-term or session) |
| `memory_list` | List all stored memories for a user |
| `memory_get` | Retrieve a specific memory by ID |
| `memory_forget` | Delete a memory by ID or query |

### Memory Scopes

| Scope | Behavior |
|-------|----------|
| **Session (short-term)** | Auto-captured during the current conversation |
| **User (long-term)** | Persists across all sessions for the user |

Auto-recall searches both scopes and presents long-term memories first.

## Verifying the Backend (Python Scripts)

The Python scripts let you test the Mem0 + FalkorDB backend directly — useful for verifying the graph store is working before connecting OpenClaw.

```bash
# Install Python dependencies
uv sync

# Quick test — add memories and search
uv run python demo_basic.py

# Full demo — multi-user isolation, updates, cleanup
uv run python demo.py
```

### `demo_basic.py` — Minimal Quick Start

Registers `mem0-falkordb`, adds memories, and searches — ~30 lines.

### `demo.py` — Comprehensive Backend Demo

| Scenario | What it demonstrates |
|----------|---------------------|
| **Add & Search** | Store facts, search with natural language queries |
| **Multi-User Isolation** | Each user gets their own FalkorDB graph — no data leaks |
| **Memory Updates** | Mem0 handles conflicting info automatically |
| **List Memories** | Inspect all stored memories for a user |
| **Cleanup** | Drop a user's entire graph with one call |

## Inspecting the Graph

Connect to FalkorDB and query the graph directly:

```bash
redis-cli -h localhost -p 6379

# List all graphs
GRAPH.LIST

# Query alice's memory graph
GRAPH.QUERY mem0_alice "MATCH (n) RETURN n LIMIT 10"

# See entity relationships
GRAPH.QUERY mem0_alice "MATCH (a)-[r]->(b) RETURN a.name, type(r), b.name"
```

## Configuration Reference

### OpenClaw Plugin Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `mode` | `"platform"` \| `"open-source"` | `"platform"` | Backend mode |
| `userId` | `string` | `"default"` | Scope memories per user |
| `autoRecall` | `boolean` | `true` | Inject memories before each turn |
| `autoCapture` | `boolean` | `true` | Store facts after each turn |
| `topK` | `number` | `5` | Max memories per recall |
| `searchThreshold` | `number` | `0.3` | Min similarity (0–1) |
| `enableGraph` | `boolean` | `false` | Entity graph (**platform mode only**) |
| `oss.graphStore.provider` | `string` | — | Graph store provider (e.g., `"falkordb"`) |
| `oss.graphStore.config` | `object` | — | `host`, `port`, `graphName`, `username`, `password` |

### FalkorDB Connection (Python scripts)

```python
config = {
    "graph_store": {
        "provider": "falkordb",
        "config": {
            "host": "localhost",       # FalkorDB host
            "port": 6379,              # FalkorDB port
            "database": "mem0",        # Graph name prefix
        },
    },
    "llm": {
        "provider": "openai",
        "config": {"model": "gpt-4o-mini"},
    },
}
```

Each user gets their own isolated graph: `{database}_{user_id}` (e.g., `mem0_alice`).

### Using FalkorDB Cloud

Replace `localhost:6379` with your cloud instance:

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

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ConnectionError` to FalkorDB | Ensure `docker compose up -d` is running and port 6379 is free |
| `OPENAI_API_KEY` error | Copy `.env.example` to `.env` and add your key |
| OpenClaw plugin not loading | Run `openclaw plugins list` to verify, then `openclaw doctor` |
| Empty search results | Verify memories were added with `openclaw mem0 stats` or `m.get_all()` |
| Python import errors | Run with `uv run` or activate the venv: `source .venv/bin/activate` |
| `register()` not called (Python) | Must call `register()` **before** `Memory.from_config()` |

## Resources

- [OpenClaw](https://github.com/openclaw/openclaw) — Personal AI assistant framework
- [OpenClaw Mem0 Plugin Docs](https://docs.mem0.ai/integrations/openclaw)
- [@falkordb/openclaw-mem0 (npm)](https://www.npmjs.com/package/@falkordb/openclaw-mem0) — FalkorDB-enabled Mem0 plugin for OpenClaw
- [@falkordb/mem0 (TypeScript)](https://github.com/FalkorDB/mem0-falkordb-ts) — FalkorDB graph store for Mem0 Node.js
- [mem0-falkordb (Python)](https://github.com/FalkorDB/mem0-falkordb) — FalkorDB graph store for Mem0 Python
- [Mem0 Node.js Graph Memory Docs](https://docs.mem0.ai/open-source/features/graph-memory)
- [FalkorDB Mem0 Integration](https://docs.falkordb.com/agentic-memory/mem0.html)
- [FalkorDB Cloud](https://app.falkordb.cloud)

## License

MIT
