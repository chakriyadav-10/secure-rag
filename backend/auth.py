import jwt
import bcrypt
import certifi
from datetime import datetime, timedelta
from config import SECRET_KEY, MONGO_URI
from pymongo import MongoClient

# Lazy connection — only connects when first needed, not at import time
_client = None
_users_collection = None

def get_users_collection():
    global _client, _users_collection
    if _users_collection is None:
        _client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(),
                              serverSelectionTimeoutMS=5000)
        _users_collection = _client['secure_rag_db']['users']
    return _users_collection

# In-memory cache for fast lookups, backed by MongoDB
blocked_users = set()

def load_blocked_users():
    """Load blocked users from DB into memory on startup"""
    try:
        users = list(get_users_collection().find({"is_blocked": True}))
        for u in users:
            blocked_users.add(u["username"])
        print(f"✅ Loaded {len(blocked_users)} blocked users into memory cache.")
    except Exception as e:
        print(f"❌ CRITICAL ERROR loading blocked users: {e}")

def block_user(username: str):
    """Permanently block a user in the database"""
    blocked_users.add(username)
    try:
        get_users_collection().update_one(
            {"username": username},
            {"$set": {"is_blocked": True}}
        )
    except:
        pass
def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

import re

def is_strong_password(password: str) -> bool:
    if len(password) < 8: return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"\d", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
    return True

def register_user(username, password, role, skip_checks=False):
    if not skip_checks and not is_strong_password(password):
        return False, "Password must be at least 8 characters long, with an uppercase letter, a number, and a special character."
        
    users = get_users_collection()
    if users.find_one({"username": username}):
        if skip_checks:
            users.update_one({"username": username}, {"$set": {"password": get_password_hash(password), "role": role}})
        return False, "Username already exists. Please choose a unique username."
        
    users.insert_one({
        "username": username,
        "password": get_password_hash(password),
        "role": role,
        "is_blocked": False
    })
    return True, "Success"

def authenticate(username, password):
    user = get_users_collection().find_one({"username": username})
    if not user:
        return None
    if user.get("is_blocked"):
        blocked_users.add(username)
        return None  # Blocked users cannot log in
    if verify_password(password, user["password"]):
        return user
    return None


def create_token(username, role):
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=3)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = data["sub"]

        # Fast cache check first
        if username in blocked_users:
            return None
            
        # Fallback to DB (Critical Fix for server restarts)
        user = get_users_collection().find_one({"username": username})
        if user and user.get("is_blocked"):
            blocked_users.add(username) # Self-healing cache
            return None
            
        return data
    except:
        return None