"""
Comprehensive demo: Mem0 + FalkorDB graph memory.

Demonstrates:
  1. Adding and searching memories
  2. Multi-user graph isolation
  3. Memory updates and evolution
  4. Listing and inspecting memories
  5. Memory history
  6. Cleanup

Prerequisites:
  1. FalkorDB running on localhost:6379  (docker compose up -d)
  2. OPENAI_API_KEY set in .env or environment
"""

import os
import sys
import time

from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not set. Copy .env.example to .env and add your key.")
    sys.exit(1)

from mem0_falkordb import register

register()

from mem0 import Memory

CONFIG = {
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


def banner(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def demo_add_and_search(m: Memory):
    banner("1. Adding and Searching Memories")

    memories = [
        "I'm a software engineer specializing in distributed systems",
        "I love hiking in the mountains and trail running",
        "My favorite programming language is Rust",
        "I'm working on a real-time data pipeline project",
        "I prefer vim over VS Code for editing",
    ]

    print("Adding memories for 'alice'...")
    for text in memories:
        m.add(text, user_id="alice")
        print(f"  + {text}")

    time.sleep(1)

    queries = [
        "what does alice do for work?",
        "what are alice's hobbies?",
        "what tools does alice use?",
    ]

    for query in queries:
        print(f"\nSearch: '{query}'")
        results = m.search(query, user_id="alice")
        for r in results.get("results", []):
            print(f"  → {r['memory']}")


def demo_multi_user(m: Memory):
    banner("2. Multi-User Graph Isolation")

    print("Adding memories for 'bob'...")
    bob_memories = [
        "Bob is a data scientist who loves Python",
        "Bob enjoys cooking Italian food",
        "Bob is training for a marathon",
    ]
    for text in bob_memories:
        m.add(text, user_id="bob")
        print(f"  + {text}")

    time.sleep(1)

    # Show isolation: same query, different users, different results
    query = "what are their hobbies?"

    print(f"\nSearch '{query}' for alice:")
    alice_results = m.search(query, user_id="alice")
    for r in alice_results.get("results", []):
        print(f"  → {r['memory']}")

    print(f"\nSearch '{query}' for bob:")
    bob_results = m.search(query, user_id="bob")
    for r in bob_results.get("results", []):
        print(f"  → {r['memory']}")

    print("\n✓ Each user has their own isolated FalkorDB graph (mem0_alice, mem0_bob)")


def demo_memory_updates(m: Memory):
    banner("3. Memory Updates and Evolution")

    print("Alice changes her favorite language...")
    m.add("I've switched from Rust to Go for my new project", user_id="alice")
    time.sleep(1)

    print("\nSearch: 'what programming language does alice use?'")
    results = m.search("what programming language does alice use?", user_id="alice")
    for r in results.get("results", []):
        print(f"  → {r['memory']}")

    print("\n✓ Mem0 handles memory evolution and conflict resolution automatically")


def demo_list_memories(m: Memory):
    banner("4. Listing All Memories")

    print("All memories for alice:")
    all_memories = m.get_all(user_id="alice")
    for mem in all_memories.get("results", []):
        print(f"  [{mem['id'][:8]}...] {mem['memory']}")

    print(f"\nTotal: {len(all_memories.get('results', []))} memories")


def demo_cleanup(m: Memory):
    banner("5. Cleanup")

    print("Deleting all memories for 'bob'...")
    m.delete_all(user_id="bob")
    print("  ✓ Bob's graph dropped")

    remaining = m.get_all(user_id="bob")
    print(f"  Bob's memories after cleanup: {len(remaining.get('results', []))}")

    print("\nDeleting all memories for 'alice'...")
    m.delete_all(user_id="alice")
    print("  ✓ Alice's graph dropped")

    print("\n✓ Cleanup complete — graphs removed from FalkorDB")


def main():
    print("Mem0 + FalkorDB Graph Memory Demo")
    print("=" * 60)
    print(f"FalkorDB: localhost:6379")
    print(f"LLM: OpenAI gpt-4o-mini")
    print(f"Graph prefix: mem0_<user_id>")

    m = Memory.from_config(CONFIG)

    try:
        demo_add_and_search(m)
        demo_multi_user(m)
        demo_memory_updates(m)
        demo_list_memories(m)
    finally:
        demo_cleanup(m)

    print("\n🎉 Demo complete!")


if __name__ == "__main__":
    main()
