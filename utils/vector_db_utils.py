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
    Applies Query Expansion to optimize vector similarity retrieval.
    """
    try:
        collection = client.get_collection(name=collection_name)
        
        # Apply Query Expansion: Append semantic descriptors if it's a short query
        search_query = query_text
        if len(query_text.split()) <= 6:
            search_query = f"{query_text} core concepts definitions process explanation overview details examples"
            logging.info(f"Query Expanded: '{query_text}' -> '{search_query}'")
            
        query_embedding = embedding_function_instance.embed_query(search_query)
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

def get_semantic_cache(query_text: str, pdf_context_name: str) -> dict:
    """
    Checks if a semantically similar query exists in the ChromaDB cache.
    Returns the cached response and suggestions if found.
    """
    try:
        cache_collection = client.get_or_create_collection(name=f"{pdf_context_name}_semantic_cache")
        # Ensure we have items before query
        if cache_collection.count() == 0:
            return None
            
        query_embedding = embedding_function_instance.embed_query(query_text)
        results = cache_collection.query(query_embeddings=[query_embedding], n_results=1)
        
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        
        if distances and distances[0] <= 0.12: # Threshold for semantic similarity
            meta = metadatas[0]
            import json
            return {
                "answer": meta.get("answer"),
                "suggestions": json.loads(meta.get("suggestions_json", "[]")),
                "citation_snippets": json.loads(meta.get("citation_snippets_json", "{}"))
            }
    except Exception as e:
        logging.error(f"Semantic cache retrieval failed: {e}")
    return None

def set_semantic_cache(query_text: str, answer: str, suggestions: list, citation_snippets: dict, pdf_context_name: str):
    """
    Saves a query, its generated answer, suggestions, and citation snippets to the ChromaDB cache.
    """
    try:
        cache_collection = client.get_or_create_collection(name=f"{pdf_context_name}_semantic_cache")
        import hashlib
        import json
        query_id = hashlib.sha256(query_text.encode("utf-8")).hexdigest()
        query_embedding = embedding_function_instance.embed_query(query_text)
        
        cache_collection.upsert(
            ids=[query_id],
            embeddings=[query_embedding],
            documents=[query_text],
            metadatas=[{
                "answer": answer,
                "suggestions_json": json.dumps(suggestions),
                "citation_snippets_json": json.dumps(citation_snippets)
            }]
        )
        logging.info(f"Cached query '{query_text}' in '{pdf_context_name}_semantic_cache'")
    except Exception as e:
        logging.error(f"Failed to cache query: {e}")