import uuid
import certifi
import base64
import re
from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI, AES_KEY

# ── AES-256 Encryption Engine ─────────────────────────────────────────────────
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os as _os

def aes_encrypt(plaintext: str) -> str:
    """Encrypt a string using AES-256-CBC. Returns base64-encoded ciphertext."""
    iv = _os.urandom(16)
    # Pad to 16-byte boundary (PKCS7)
    pad_len = 16 - (len(plaintext.encode()) % 16)
    padded = plaintext.encode() + bytes([pad_len] * pad_len)
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(iv + ct).decode()

def aes_decrypt(ciphertext_b64: str) -> str:
    """Decrypt a base64-encoded AES-256-CBC ciphertext back to plaintext."""
    raw = base64.b64decode(ciphertext_b64)
    iv, ct = raw[:16], raw[16:]
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()
    pad_len = padded[-1]
    return padded[:-pad_len].decode()

# ── MongoDB Connection (Lazy) ─────────────────────────────────────────────────
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
            # AES-256 encrypt the original PII before storing in MongoDB
            encrypted_val = aes_encrypt(val)
            get_mappings_col().insert_one({
                "token": token,
                "original": encrypted_val,   # Encrypted — not readable in DB
                "category": category,
                "owner_id": owner_id,
                "encrypted": True,
                "created_at": datetime.utcnow()
            })
            text = text.replace(val, token)

    return text

def lookup_token(token, owner_id):
    """Reverse-lookup: only allows the real owner to decrypt their own token."""
    record = get_mappings_col().find_one({"token": token, "owner_id": owner_id})
    if not record:
        return None
    try:
        return aes_decrypt(record["original"])
    except Exception:
        # Fallback for old records stored before AES was implemented
        return record["original"]

def depseudonymize(text, owner_id):
    """Replace all pseudonym tokens in the text with real values — only for the owner."""
    # Find all tokens like ACCOUNT_f7ce, EMAIL_a1b2, PHONE_x9y8, IFSC_m3n4
    tokens = re.findall(r"((?:ACCOUNT|EMAIL|PHONE|IFSC)_[a-f0-9]{6})", text, re.IGNORECASE)
    for token in tokens:
        original = lookup_token(token, owner_id)
        if original:
            text = text.replace(token, original)
    return text