
from chromadb import Client
import ollama

client = Client()
collection = client.create_collection("agent_memory")

def embed(text):
    return ollama.embeddings(model="nomic-embed-text", prompt=text)["embedding"]

# Add memory
msg = "Agent observing user intent."
collection.add(documents=[msg], embeddings=[embed(msg)], ids=["1"])

# Query memory
query = "What did the agent observe?"
results = collection.query(query_embeddings=[embed(query)], n_results=3)

print("Retrieved:", results)
