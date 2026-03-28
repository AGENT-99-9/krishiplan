import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'krishisarthi.settings')
# django.setup() # Not strictly needed if not using DB models directly in this script, but good practice

from ml.rag.rag_engine import RAGEngine

def test():
    engine = RAGEngine()
    query = "What is the recommended fertilizer for wheat in Punjab?"
    print(f"User Query: {query}")
    print("-" * 50)
    
    result = engine.query(query)
    
    print(f"Sub-Queries: {result['sub_queries']}")
    print("-" * 50)
    print(f"Answer: {result['answer']}")
    print("-" * 50)
    print("Sources:")
    for src in result['sources']:
        print(f" - {src['name']} (Score: {src['score']})")

if __name__ == "__main__":
    test()
