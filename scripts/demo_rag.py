
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.embeddings.generator import EmbeddingGenerator
from vector_store.chroma.client import NewsVectorStore

logging.basicConfig(level=logging.ERROR) # Quiet logs

def run_rag_demo():
    print("\n🔍 --- News Intelligence Search (RAG) ---")
    
    # 1. Load Models
    print("⏳ Loading AI Models... (Please wait)")
    embedder = EmbeddingGenerator()
    vector_store = NewsVectorStore()
    
    # 2. Define Query
    queries = [
        "What is happening with the weather?",
        "Tell me about political protests.",
        "Any news about Donald Trump?"
    ]
    
    for q in queries:
        print(f"\n❓ Query: '{q}'")
        
        # A. Vectorize Query
        query_vector = embedder.generate(q)
        
        # B. Search Vector DB
        results = vector_store.search(query_vector, n_results=2)
        
        # C. Display Results
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                print(f"   📄 Result {i+1}:")
                print(f"      Title:  {meta['title']}")
                print(f"      Source: {meta['source']}")
                print(f"      Snippet: {doc[:100]}...")
        else:
            print("   ❌ No results found.")

    print("\n✅ Demo Complete.")

if __name__ == "__main__":
    run_rag_demo()
