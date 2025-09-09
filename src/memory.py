import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional

class MemorySystem:
    def __init__(self, persist_directory: str = "./data"):
        # Set up ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Load the embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Create or get the collection for memories
        self.collection = self.client.get_or_create_collection(
            name="agent_memories",
            metadata={"description": "Agent's long-term memory for interactions and preferences"}
        )

    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for the given text."""
        return self.embedding_model.encode(text).tolist()

    def store_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Store a memory with its embedding."""
        embedding = self.embed_text(text)
        id = str(len(self.collection.get()['ids']) + 1)  # Simple ID generation
        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata] if metadata else [{}],
            ids=[id]
        )

    def retrieve_relevant_memories(self, query: str, n_results: int = 5):
        """Retrieve relevant memories based on semantic search."""
        query_embedding = self.embed_text(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

    def get_all_memories(self):
        """Get all stored memories."""
        return self.collection.get()

    def store_interaction(self, user_input: str, agent_response: str):
        """Store user input and agent response as a memory."""
        memory_text = f"User: {user_input}\nAgent: {agent_response}"
        metadata = {
            "type": "interaction",
            "user_input": user_input,
            "agent_response": agent_response
        }
        self.store_memory(memory_text, metadata)

    def get_context_for_query(self, query: str, n_results: int = 3) -> str:
        """Retrieve relevant context for a query and format it."""
        results = self.retrieve_relevant_memories(query, n_results)
        context = ""
        if results['documents']:
            context = "Relevant past interactions:\n"
            for doc in results['documents'][0]:
                context += f"- {doc}\n"
        return context

# Global instance
memory_system = MemorySystem()