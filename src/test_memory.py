from memory import memory_system

# Test storing sample data
print("Storing sample memories...")
memory_system.store_memory("User prefers Python for coding.", {"type": "preference", "topic": "coding"})
memory_system.store_memory("User asked about machine learning basics.", {"type": "query", "topic": "ML"})
memory_system.store_interaction("What is ChromaDB?", "ChromaDB is a vector database for embeddings.")

# Test retrieving
print("\nRetrieving relevant memories for 'coding preferences'...")
results = memory_system.retrieve_relevant_memories("coding preferences")
if results['documents']:
    for doc in results['documents'][0]:
        print(f"- {doc}")

print("\nRetrieving context for 'machine learning'...")
context = memory_system.get_context_for_query("machine learning")
print(context)

print("\nAll memories:")
all_mem = memory_system.get_all_memories()
for i, doc in enumerate(all_mem['documents']):
    print(f"{i+1}: {doc}")