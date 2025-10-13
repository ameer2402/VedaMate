import chromadb
import logging
import os
from typing import List, Dict, Any
from .config import CHROMA_PERSIST_DIRECTORY, TOP_K
from .embeddings import get_embedding_function
from .pdf_processor import process_pdf

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIRECTORY)
embedding_function_instance = get_embedding_function()

def process_and_store_pdf(pdf_path: str, collection_name: str):
    """
    Processes a PDF, creates embeddings, and stores them in a ChromaDB collection.
    """
    try:
        if collection_name in [c.name for c in client.list_collections()]:
            logging.info(f"Collection '{collection_name}' already exists. Skipping processing.")
            return

        filename = os.path.basename(pdf_path)
        chunks = process_pdf(pdf_path, filename)
        if not chunks:
            return

        texts = [chunk.page_content for chunk in chunks]
        embeddings = embedding_function_instance.embed_documents(texts)
        collection = client.create_collection(name=collection_name)
        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        metadatas = [chunk.metadata for chunk in chunks]

        collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
        logging.info(f"Successfully stored '{filename}' in ChromaDB collection '{collection_name}'.")
    except Exception as e:
        logging.error(f"Failed to process/store PDF for collection '{collection_name}': {e}")
        raise

async def query_vector_db(query_text: str, collection_name: str) -> Dict[str, Any]:
    """
    Queries ChromaDB and returns a structured context string with explicit page numbers for citation.
    """
    try:
        collection = client.get_collection(name=collection_name)
        query_embedding = embedding_function_instance.embed_query(query_text)
        results = collection.query(query_embeddings=[query_embedding], n_results=TOP_K)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        # NEW: Build a structured context string for the LLM
        structured_context_parts = []
        for doc, meta in zip(documents, metadatas):
            page = meta.get('page', 'N/A')
            # Create a formatted block for each retrieved chunk that the LLM can easily parse
            context_block = f"Source Page: {page}\nContent: {doc}"
            structured_context_parts.append(context_block)

        context_text = "\n\n---\n\n".join(structured_context_parts)
        
        # We still return the raw sources list for potential future use, but it's not the primary context anymore
        sources = [f"{meta['source']} (Page {meta.get('page', 'N/A')})" for meta in metadatas]
        
        return {"context_text": context_text, "sources": sources}
    except Exception as e:
        logging.error(f"Failed to query ChromaDB collection '{collection_name}': {e}")
        return {"context_text": "", "sources": []}