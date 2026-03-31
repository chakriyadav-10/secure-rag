from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI
import certifi

_client = None
_audit_collection = None

def get_audit_collection():
    global _client, _audit_collection
    if _audit_collection is None:
        _client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        _audit_collection = _client['secure_rag_db']['audit_logs']
    return _audit_collection

def log_event(username: str, action: str, details: str, status: str = "SUCCESS"):
    """
    LIMITATION FIX: Audit Logging & Compliance Dashboard
    Logs security events and system actions for SIEM compliance.
    """
    try:
        log_entry = {
            "timestamp": datetime.utcnow(),
            "username": username,
            "action": action,
            "details": details,
            "status": status
        }
        get_audit_collection().insert_one(log_entry)
        print(f"📝 [AUDIT LOG] {username} | {action} | {status}")
    except Exception as e:
        print(f"⚠️ Audit Log Failed: {e}")
