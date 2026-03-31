import uuid
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
    index.upsert(
        vectors=[
            {"id": doc_id, "values": vec, "metadata": {"text": text, "owner_id": owner_id}}
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
    # Only return chunks that are genuinely relevant to the query
    return [
        match['metadata']['text']
        for match in response['matches']
        if match['score'] >= RELEVANCE_THRESHOLD
    ]