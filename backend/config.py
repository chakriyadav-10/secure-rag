import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
BLOCK_THRESHOLD = int(os.getenv("BLOCK_THRESHOLD", 3))
MASTER_ADMIN_USER = os.getenv("MASTER_ADMIN_USER", "admin")
MASTER_ADMIN_PASS = os.getenv("MASTER_ADMIN_PASS", "admin123")

# Cloud Database Configurations
MONGO_URI = os.getenv("MONGO_URI", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "secure-rag-index")

# AES-256 Key for PII Field-Level Encryption (must be 32 bytes for AES-256)
# Falls back to a SHA-256 hash of SECRET_KEY if no dedicated key is set
import hashlib
_raw_aes = os.getenv("AES_ENCRYPTION_KEY", "")
if _raw_aes:
    AES_KEY = hashlib.sha256(_raw_aes.encode()).digest()
else:
    AES_KEY = hashlib.sha256(SECRET_KEY.encode()).digest()