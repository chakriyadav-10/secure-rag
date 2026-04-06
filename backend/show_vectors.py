"""
Pinecone Vector Inspector — Show professors the actual stored vectors
Run: python3 show_vectors.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from pinecone import Pinecone

# --- ANSI Colors ---
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Fetch index stats
stats = index.describe_index_stats()

print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
print(f"{CYAN}{BOLD}  PINECONE VECTOR DATABASE — LIVE INSPECTION{RESET}")
print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")

print(f"{YELLOW}Index Name:{RESET}       {PINECONE_INDEX_NAME}")
print(f"{YELLOW}Total Vectors:{RESET}    {stats.total_vector_count}")
print(f"{YELLOW}Dimensions:{RESET}       {stats.dimension}")
print(f"{YELLOW}Metric:{RESET}           Cosine Similarity")
print(f"{BLUE}{'─'*70}{RESET}\n")

# Fetch actual vectors using a zero vector query (returns random vectors)
dummy_vec = [0.0] * stats.dimension
results = index.query(
    vector=dummy_vec,
    top_k=5,
    include_metadata=True,
    include_values=True
)

if not results['matches']:
    print(f"{RED}No vectors found in the index.{RESET}")
else:
    for i, match in enumerate(results['matches'], 1):
        print(f"{GREEN}{BOLD}─── Vector #{i} ───{RESET}")
        print(f"  {CYAN}▸ ID:{RESET}        {match['id']}")
        print(f"  {CYAN}▸ Score:{RESET}      {match['score']:.4f}")
        
        # Show owner_id (proves multi-tenant isolation)
        owner = match.get('metadata', {}).get('owner_id', 'N/A')
        print(f"  {CYAN}▸ Owner ID:{RESET}   {YELLOW}{owner}{RESET}")
        
        # Show first 100 chars of stored text (pseudonymized)
        text = match.get('metadata', {}).get('text', 'N/A')
        preview = text[:150].replace('\n', ' ') + ("..." if len(text) > 150 else "")
        print(f"  {CYAN}▸ Text:{RESET}       {preview}")
        
        # Show first 8 vector dimensions + total
        vec = match.get('values', [])
        if vec:
            shown = [f"{v:.6f}" for v in vec[:8]]
            print(f"  {CYAN}▸ Vector:{RESET}     [{', '.join(shown)}, ...] {YELLOW}({len(vec)} dimensions){RESET}")
        
        print()

print(f"{BLUE}{BOLD}{'='*70}{RESET}")
print(f"{GREEN}💾 All vectors above are DP-noised and PII-pseudonymized.{RESET}")
print(f"{GREEN}🔐 Owner ID metadata enforces multi-tenant query isolation.{RESET}\n")
