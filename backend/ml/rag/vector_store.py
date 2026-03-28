import os
import logging
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional

# Suppress annoying HuggingFace / Transformers warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent          # backend/
CHROMA_PERSIST_DIR = str(BASE_DIR / "ml" / "rag" / "chroma_db")

# ── Embedding Model ───────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"      # 384-dim, ~80 MB, CPU-fast
COLLECTION_NAME = "krishisarthi_agri_docs"

# ── Singleton ─────────────────────────────────────────────

_client: Optional[chromadb.ClientAPI] = None
_collection = None
_embed_fn = None

def _get_embed_fn():
    global _embed_fn
    if _embed_fn is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embed_fn = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL,
            device="cpu",
        )
    return _embed_fn

def get_collection():
    """Return (or create) the persistent ChromaDB collection."""
    global _client, _collection

    if _collection is not None:
        return _collection

    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

    _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    _collection = _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_get_embed_fn(),
        metadata={"hnsw:space": "cosine"},      # cosine similarity
    )

    logger.info(
        f"ChromaDB collection '{COLLECTION_NAME}' ready  "
        f"({_collection.count()} docs)  persist={CHROMA_PERSIST_DIR}"
    )
    return _collection

def upsert_chunks(chunks: List[Dict[str, Any]]) -> int:
    """Insert or update a batch of structured chunks into the vector store."""
    col = get_collection()

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        uid = f"{chunk['doc_id']}::chunk_{chunk['chunk_id']}"
        raw_text = chunk["text"]

        meta = {
            "doc_id":             chunk.get("doc_id", ""),
            "chunk_id":           str(chunk.get("chunk_id", "")),
            "document_name":      chunk.get("document_name", ""),
            "page_numbers":       str(chunk.get("page_numbers", [])),
            "primary_topic":      chunk.get("primary_topic", "Research"),
            "crop_entities":      ", ".join(chunk.get("crop_entities", [])),
            "practice_entities":  ", ".join(chunk.get("practice_entities", [])),
            "region_entities":    ", ".join(chunk.get("region_entities", [])),
            "numeric_signals":    ", ".join(chunk.get("numeric_signals", [])),
            "relevance_score":    float(chunk.get("relevance_score", 0.0)),
            "char_count":         len(raw_text),
            "raw_text":           raw_text,
        }

        ids.append(uid)
        documents.append(raw_text) # Simple for now
        metadatas.append(meta)

    BATCH = 100
    total = 0
    for i in range(0, len(ids), BATCH):
        col.upsert(
            ids=ids[i:i+BATCH],
            documents=documents[i:i+BATCH],
            metadatas=metadatas[i:i+BATCH],
        )
        total += len(ids[i:i+BATCH])
    
    return total

def search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Semantic search."""
    col = get_collection()

    results = col.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    if results and results["ids"] and results["ids"][0]:
        for idx in range(len(results["ids"][0])):
            dist = results["distances"][0][idx] if results["distances"] else 1.0
            score = 1.0 - dist
            meta = results["metadatas"][0][idx] if results["metadatas"] else {}
            text = results["documents"][0][idx] if results["documents"] else ""

            hits.append({
                "text": text,
                "score": round(score, 4),
                **meta,
            })

    return hits
