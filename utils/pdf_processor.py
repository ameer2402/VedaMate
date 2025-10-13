from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from .config import PDF_CHUNK_SIZE, PDF_CHUNK_OVERLAP
import logging
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO)

def process_pdf(pdf_path: str, filename: str) -> List[Document]:
    """
    Processes a PDF file from a given path, extracts text, and splits it into chunks.
    """
    try:
        reader = PdfReader(pdf_path)
        documents = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                documents.append(
                    Document(
                        page_content=text,
                        metadata={"page": page_num + 1, "source": filename},
                    )
                )
        
        if not documents:
            logging.warning(f"No text content extracted from {filename}")
            return []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=PDF_CHUNK_SIZE,
            chunk_overlap=PDF_CHUNK_OVERLAP,
        )
        chunks = text_splitter.split_documents(documents)
        logging.info(f"Split {filename} into {len(chunks)} chunks.")
        return chunks
    except Exception as e:
        logging.error(f"Error processing PDF {filename}: {str(e)}")
        raise