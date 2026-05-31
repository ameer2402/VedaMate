import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_embedding_function():
    """
    Initializes and returns a Google Generative AI model for creating embeddings.
    Consumes 0MB of local RAM, making it compatible with free-tier hosting.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=api_key
    )