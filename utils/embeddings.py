from langchain_huggingface import HuggingFaceEmbeddings
from .config import EMBEDDING_MODEL_NAME

def get_embedding_function():
    """
    Initializes and returns a sentence-transformer model for creating embeddings locally.
    Runs on the CPU to completely bypass any API rate limits.
    """
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )