# from langchain_community.embeddings import HuggingFaceEmbeddings
# from .config import EMBEDDING_MODEL_NAME

# def get_embedding_function():
#     """
#     Initializes and returns a sentence-transformer model for creating embeddings.
#     Runs on the CPU.
#     """
#     model_kwargs = {'device': 'cpu'}
#     encode_kwargs = {'normalize_embeddings': False}
#     return HuggingFaceEmbeddings(
#         model_name=EMBEDDING_MODEL_NAME,
#         model_kwargs=model_kwargs,
#         encode_kwargs=encode_kwargs
#     )

# utils/embeddings.py
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from .config import GOOGLE_EMBEDDING_MODEL_NAME
import os

def get_embedding_function():
    """
    Initializes and returns the Google Generative AI embedding model.
    """
    return GoogleGenerativeAIEmbeddings(
        model=GOOGLE_EMBEDDING_MODEL_NAME,
        google_api_key=os.environ.get("GOOGLE_API_KEY")
    )