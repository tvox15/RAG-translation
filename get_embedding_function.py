import openai
import os
from langchain.embeddings.openai import OpenAIEmbeddings

EMBEDDING_MODEL="text-embedding-3-large"

if os.getenv("OPENAI_API_KEY") is not None:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print ("OPENAI_API_KEY is ready")
else:
    print ("OPENAI_API_KEY environment variable not found")

def get_embedding_function():
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=openai.api_key
    )
    return embeddings