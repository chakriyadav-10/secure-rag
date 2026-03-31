import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
BLOCK_THRESHOLD = int(os.getenv("BLOCK_THRESHOLD", 3))

# Cloud Database Configurations
MONGO_URI = os.getenv("MONGO_URI", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "secure-rag-index")