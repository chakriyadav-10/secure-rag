import uuid
from pseudo import aes_encrypt, aes_decrypt
from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX_NAME

pc = Pinecone(api_key=PINECONE_API_KEY)

EMBEDDING_DIM = 3072  # gemini-embedding-001

existing = pc.list_indexes().names()
if PINECONE_INDEX_NAME in existing:
    # Check if dimension matches; delete and recreate if not
    desc = pc.describe_index(PINECONE_INDEX_NAME)
    if desc.dimension != EMBEDDING_DIM:
        print(f"⚠️  Pinecone index dimension mismatch ({desc.dimension} vs {EMBEDDING_DIM}). Recreating index...")
        pc.delete_index(PINECONE_INDEX_NAME)
        existing = []

if PINECONE_INDEX_NAME not in existing:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region=PINECONE_ENV)
    )
    print(f"✅ Created Pinecone index '{PINECONE_INDEX_NAME}' with {EMBEDDING_DIM} dimensions.")

index = pc.Index(PINECONE_INDEX_NAME)

def add_doc(vec, text, owner_id):
    doc_id = str(uuid.uuid4())
    # 🔐 Encrypt the text chunk before storing in Pinecone (Zero-Trust Metadata)
    encrypted_text = aes_encrypt(text)
    index.upsert(
        vectors=[
            {
                "id": doc_id, 
                "values": vec, 
                "metadata": {
                    "text": encrypted_text, 
                    "owner_id": owner_id,
                    "is_encrypted": True # Flag for future-proofing
                }
            }
        ]
    )

RELEVANCE_THRESHOLD = 0.5   # Min cosine similarity to treat a doc chunk as relevant

def search(vec, owner_ids):
    response = index.query(
        vector=vec,
        top_k=3,
        include_metadata=True,
        filter={"owner_id": {"$in": owner_ids}}
    )
    
    results = []
    for match in response['matches']:
        if match['score'] >= RELEVANCE_THRESHOLD:
            raw_text = match['metadata']['text']
            # Fallback logic: identify if it is ciphertext or legacy plain-text
            # Encrypted text is usually much longer than raw snippets in our bank doc
            if match['metadata'].get("is_encrypted") or len(raw_text) > 40:
                try:
                    decrypted = aes_decrypt(raw_text)
                    results.append(decrypted)
                except Exception:
                    # Not actually encrypted, handle as legacy
                    results.append(raw_text)
            else:
                results.append(raw_text)
                
    return results
