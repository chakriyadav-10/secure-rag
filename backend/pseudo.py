import uuid
import certifi
from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI

# Lazy connection — only connects when first needed
_client = None
_mappings_col = None

def get_mappings_col():
    global _client, _mappings_col
    if _mappings_col is None:
        _client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(),
                              serverSelectionTimeoutMS=5000)
        _mappings_col = _client["secure_rag_db"]["pii_mappings"]
    return _mappings_col

# Process in priority order: specific patterns first, broad patterns last
PRIORITY_ORDER = ["email", "ifsc", "phone", "account"]

def pseudonymize(text, pii_data, owner_id="unknown"):
    ordered = {k: pii_data[k] for k in PRIORITY_ORDER if k in pii_data}
    for k, v in pii_data.items():
        if k not in ordered:
            ordered[k] = v

    seen = set()
    for category, values in ordered.items():
        for val in values:
            if val in seen or not val:
                continue
            seen.add(val)
            token = f"{category.upper()}_{str(uuid.uuid4())[:6]}"
            # Persist to MongoDB with owner tracking
            get_mappings_col().insert_one({
                "token": token,
                "original": val,
                "category": category,
                "owner_id": owner_id,
                "created_at": datetime.utcnow()
            })
            text = text.replace(val, token)

    return text

def lookup_token(token, owner_id):
    """Reverse-lookup: only allows owner to decrypt their own token."""
    record = get_mappings_col().find_one({"token": token, "owner_id": owner_id})
    return record["original"] if record else None