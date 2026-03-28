import os
import json
import logging
from pathlib import Path
from pypdf import PdfReader
from .vector_store import upsert_chunks

logger = logging.getLogger(__name__)

# ==============================
# CONFIG
# ==============================

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
CHUNK_SIZE = 1000  # Chars
CHUNK_OVERLAP = 200

# ==============================
# PDF EXTRACTOR
# ==============================

def extract_text_from_pdf(pdf_path):
    """Extract and chunk text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        source_name = os.path.basename(pdf_path)
        doc_id = source_name.replace(".pdf", "").replace(" ", "_").lower()
        
        chunks = []
        chunk_counter = 1
        
        all_text = ""
        page_char_map = [] # stores (char_index, page_number)

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            
            # Record page numbers for char indices
            start_idx = len(all_text)
            all_text += text + "\n\n"
            end_idx = len(all_text)
            page_char_map.append((start_idx, end_idx, page_num + 1))

        # Chunking
        for start in range(0, len(all_text), CHUNK_SIZE - CHUNK_OVERLAP):
            end = start + CHUNK_SIZE
            chunk_text = all_text[start:end].strip()
            
            if len(chunk_text) < 50:
                continue
            
            # Map chunk to page numbers
            pages = []
            for s_idx, e_idx, p_num in page_char_map:
                if (start >= s_idx and start < e_idx) or (end > s_idx and end <= e_idx) or (start <= s_idx and end >= e_idx):
                    pages.append(p_num)
            
            chunks.append({
                "doc_id": doc_id,
                "chunk_id": str(chunk_counter),
                "document_name": source_name,
                "page_numbers": sorted(list(set(pages))),
                "text": chunk_text
            })
            chunk_counter += 1
            
        return chunks
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {e}")
        return []

# ==============================
# MAIN INGESTOR
# ==============================

def ingest_all():
    """Process all PDFs in ml/docs and upsert to ChromaDB."""
    if not os.path.exists(DOCS_DIR):
        print(f"Directory {DOCS_DIR} not found.")
        return

    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF documents in {DOCS_DIR}")
    
    total_chunks = 0
    for pdf in pdf_files:
        pdf_path = DOCS_DIR / pdf
        print(f"Processing: {pdf}...")
        
        chunks = extract_text_from_pdf(pdf_path)
        if chunks:
            count = upsert_chunks(chunks)
            total_chunks += count
            print(f"  - Generated {count} chunks for {pdf}")
        else:
            print(f"  - No text extracted for {pdf}")
            
    print(f"\n✅ SUCCESS: Refreshed knowledge base with {total_chunks} total chunks.")

if __name__ == "__main__":
    ingest_all()
