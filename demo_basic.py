"""
Minimal quick-start: Mem0 + FalkorDB graph memory.

Prerequisites:
  1. FalkorDB running on localhost:6379  (docker compose up -d)
  2. OPENAI_API_KEY set in .env or environment
"""

from dotenv import load_dotenv

load_dotenv()

# Register FalkorDB as a graph store provider (must be called before Memory)
from mem0_falkordb import register

register()

from mem0 import Memory

config = {
    "graph_store": {
        "provider": "falkordb",
        "config": {
            "host": "localhost",
            "port": 6379,
            "database": "mem0",
        },
    },
    "llm": {
        "provider": "openai",
        "config": {"model": "gpt-4o-mini"},
    },
}

m = Memory.from_config(config)

# Store some memories
print("Adding memories...")
m.add("I love hiking and trail running", user_id="alice")
m.add("Alice is a software engineer at a startup", user_id="alice")
m.add("Alice is learning Rust and enjoys systems programming", user_id="alice")

# Search memories
print("\nSearching: 'what are alice's hobbies?'")
results = m.search("what are alice's hobbies?", user_id="alice")
for r in results.get("results", []):
    print(f"  - {r['memory']}")

# List all memories
print("\nAll memories for alice:")
all_memories = m.get_all(user_id="alice")
for mem in all_memories.get("results", []):
    print(f"  [{mem['id'][:8]}] {mem['memory']}")

print("\nDone! Check FalkorDB graph at localhost:6379 (graph: mem0_alice)")
