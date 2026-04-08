from config import GEMINI_API_KEY
from db import add_doc, search
from dp_embedding import protect_embedding   # Embedding inversion defence
from xai_citations import generate_xai_prompt # Limitation Fix

# Lazy client instance to prevent blocking server boot
_rag_client = None

def get_client():
    global _rag_client
    if _rag_client is None:
        from google import genai
        from google.genai import types
        _rag_client = (genai.Client(api_key=GEMINI_API_KEY), types)
    return _rag_client

def embed(text):
    client, types = get_client()
    response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    return response.embeddings[0].values

def embed_query(text):
    client, types = get_client()
    response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    return response.embeddings[0].values

def store(text, owner_id):
    vec = embed(text)
    noisy_vec = protect_embedding(vec)   # DP noise from dp_embedding.py
    add_doc(noisy_vec, text, owner_id)

def retrieve(query, owner_ids):
    vec = embed_query(query)
    return search(vec, owner_ids)

def generate(query, context):
    client, types = get_client()
    # Use the new XAI Prompt Generator
    prompt = generate_xai_prompt(query, context)

    response = client.models.generate_content(
        model="models/gemini-flash-lite-latest",
        contents=prompt
    )
    
    text = response.text.strip()
    source = "🤖 Gemini General Knowledge"  # Default fallback
    
    # Parse the dynamic source tag provided by the LLM
    if text.startswith("[SOURCE:"):
        end_idx = text.find("]")
        if end_idx != -1:
            source_tag = text[8:end_idx].strip()
            if "Uploaded" in source_tag:
                source = "📄 Uploaded Documents"
            text = text[end_idx+1:].strip()

    return text, source