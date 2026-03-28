import os
import json
import logging
from typing import List, Dict, Any, Optional
from .vector_store import search as vector_search
from .utility import call_llm

logger = logging.getLogger(__name__)

# ── Prompt Templates ──────────────────────────────────────

DISINTEGRATION_PROMPT = """You are an AI agricultural assistant. Your task is to break down a complex user query into a series of smaller, sequential sub-queries that maintain context and flow.

Each sub-query should:
1. Focus on a specific aspect of the original query.
2. Build upon the context of previous sub-queries.
3. Help in extracting more precise context from a knowledge base.

Guidelines:
- Return ONLY a JSON list of strings (sub-queries).
- Each sub-query should be a complete sentence.
- The sub-queries should lead to a final sub-query that is a "smaller image" of the original query but highly specific.
- Example: "How to grow rice in Punjab using DAP?" 
  Sub-queries: ["What are the general climatic requirements for rice cultivation in Punjab?", "How do Punjab's soil conditions affect rice nutrient needs?", "What is the recommended dosage and application time for DAP in Punjab's rice varieties?"]

USER QUERY: {query}

JSON RESPONSE:"""

SYSTEM_PROMPT = """You are **KrishiSaarthi AI**, a professional agriculture advisor for Indian farmers.
Answer the user's question accurately using ONLY the provided context from the knowledge base.
If the context is insufficient, explain what's missing.

IMPORTANT RULES:
- Do NOT mention document names, source numbers (like [1]), or citations in your answer text. 
- I will display the sources separately to the user. 
- Focus entirely on providing a clean, expert response.
- Always be polite, practical, and use Indian farming terminology where appropriate."""

RAG_PROMPT_TEMPLATE = """{system}

─── CONTEXT DOCUMENTS ───
{context_block}
─── END CONTEXT ───

USER QUESTION: {query}

Provide a well-structured, evidence-based answer using the context above. End with a practical tip."""

class RAGEngine:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def disintegrate_query(self, query: str) -> List[str]:
        """Break down the query into sub-queries for better retrieval."""
        try:
            prompt = DISINTEGRATION_PROMPT.format(query=query)
            raw_response = call_llm(prompt, require_json=True)
            
            if not raw_response:
                return [query]
                
            # Parse JSON
            sub_queries = []
            try:
                sub_queries = json.loads(raw_response)
            except:
                # Fallback extraction
                import re
                matches = re.findall(r'"([^"]*)"', raw_response)
                if matches:
                    sub_queries = matches
            
            if not isinstance(sub_queries, list) or not sub_queries:
                return [query]
                
            logger.info(f"Disintegrated query into: {sub_queries}")
            return sub_queries
        except Exception as e:
            logger.error(f"Query disintegration failed: {e}")
            return [query]

    def retrieve_context(self, sub_queries: List[str]) -> List[Dict[str, Any]]:
        """Retrieve context for each sub-query and deduplicate."""
        all_hits = []
        seen_texts = set()
        
        # We fetch fewer chunks per sub-query but cover more ground
        k_per_query = max(2, self.top_k // (len(sub_queries) if sub_queries else 1))
        
        for q in sub_queries:
            hits = vector_search(q, top_k=k_per_query)
            for h in hits:
                if h["text"] not in seen_texts:
                    seen_texts.add(h["text"])
                    all_hits.append(h)
                    
        return all_hits

    def _build_context_block(self, hits: List[Dict[str, Any]]) -> str:
        if not hits:
            return "(No relevant documents found.)"
            
        blocks = []
        for i, hit in enumerate(hits, 1):
            text = hit.get("raw_text", hit.get("text", ""))
            blocks.append(f"─── KNOWLEDGE CHUNK {i} ───\n{text}")
            
        return "\n\n".join(blocks)

    def query(self, user_query: str) -> Dict[str, Any]:
        """Full RAG pipeline: disintegrate -> retrieve -> generate."""
        # 1. Disintegrate
        sub_queries = self.disintegrate_query(user_query)
        
        # 2. Retrieve for all sub-queries
        hits = self.retrieve_context(sub_queries)
        
        # 3. Build Prompt
        context_block = self._build_context_block(hits)
        prompt = RAG_PROMPT_TEMPLATE.format(
            system=SYSTEM_PROMPT,
            context_block=context_block,
            query=user_query
        )
        
        # 4. Generate
        answer = call_llm(prompt)
        
        if not answer:
            answer = "I apologize, but I'm having trouble connecting to my knowledge base right now."
            
        # 5. Extract sources
        sources = []
        seen_docs = set()
        for h in hits:
            doc = h.get("document_name")
            if doc and doc not in seen_docs:
                seen_docs.add(doc)
                sources.append({
                    "name": doc,
                    "pages": h.get("page_numbers"),
                    "score": h.get("score")
                })
                
        return {
            "query": user_query,
            "sub_queries": sub_queries,
            "answer": answer,
            "sources": sources,
            "chunks_used": len(hits)
        }
