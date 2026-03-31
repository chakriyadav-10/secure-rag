from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import io, re
from PyPDF2 import PdfReader
from auth import register_user, authenticate, blocked_users, create_token, verify_token, block_user, load_blocked_users, get_users_collection
from security import detect_threat, sanitize
from pii_detector import detect_pii
from pseudo import pseudonymize
from rag import store, retrieve, generate
from config import BLOCK_THRESHOLD

from audit_logger import log_event, get_audit_collection
from rate_limiter import check_rate_limit
from xai_citations import format_chunk_with_citation

# ── Banking topic filter ──────────────────────────────────────────────────────
# Keyword-based check is far more reliable than asking a lite LLM to self-restrict.
BANKING_KEYWORDS = {
    "bank", "account", "loan", "credit", "debit", "finance", "financial",
    "interest", "rate", "emi", "deposit", "withdraw", "transfer", "payment",
    "insurance", "invest", "investment", "mutual", "fund", "stock", "share",
    "neft", "rtgs", "imps", "upi", "ifsc", "kyc", "atm", "mortgage",
    "savings", "current", "fd", "fixed", "rd", "recurring", "cheque",
    "draft", "sbi", "hdfc", "icici", "axis", "kotak", "rbi", "sebi",
    "nbfc", "microfinance", "pension", "ppf", "nps", "tax", "gst", "pan",
    "aadhaar", "nominee", "passbook", "statement", "balance", "transaction",
    "forex", "currency", "exchange", "swift", "iban", "money", "cash",
    "open", "apply", "eligibility", "document", "interest", "repay",
}

def is_banking_query(text):
    words = set(re.findall(r"\w+", text.lower()))
    return bool(words & BANKING_KEYWORDS)

app = FastAPI()

@app.on_event("startup")
def startup_event():
    try:
        register_user("admin", "admin123", "admin")
        load_blocked_users() # LIMITATION FIX: Persistent Blocks
    except Exception as e:
        print("Warning: Could not seed master admin:", e)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
def register(username: str, password: str, role: str = "user"):
    # LIMITATION FIX: Hardcode role to "user" to prevent Mass Assignment (IDOR) attacks.
    # Even if a hacker passes ?role=admin, the backend completely ignores it.
    register_user(username, password, "user")
    return {"msg": "Registered"}

@app.post("/login")
def login(username: str, password: str):
    user = authenticate(username, password)
    if user:
        token = create_token(username, user["role"])
        return {"token": token, "role": user["role"], "username": username}
    return {"error": "Invalid credentials"}

def authorize(token):
    data = verify_token(token)
    if not data:
        raise Exception("Unauthorized")
    return data

@app.post("/upload")
async def upload(file: UploadFile, token: str):
    user = authorize(token)
    
    # Limitation Fix: DoS Protection via Rate Limiter
    check_rate_limit(user["sub"])
    
    owner_id = "admin" if user.get("role") == "admin" else user["sub"]

    content_parts = []
    if file.filename.endswith(".pdf"):
        pdf = PdfReader(io.BytesIO(await file.read()))
        for i, page in enumerate(pdf.pages):
            t = page.extract_text()
            if t: 
                # Limitation Fix: XAI Citations (Tagging text with Page numbers)
                cited_text = format_chunk_with_citation(str(t), page_num=i+1)
                content_parts.append(cited_text)
        content = "\n".join(content_parts)
    else:
        content = (await file.read()).decode('utf-8', errors='ignore')

    # 🚨 Threat Detection
    is_threat, threat_type = detect_threat(content)
    if is_threat:
        if user["sub"] != "admin": # LIMITATION FIX: Master admin immunity
            block_user(user["sub"])
            
        msg = "🔴 Prompt injection detected in document. User blocked." if threat_type == "prompt_injection" else "🔴 Malicious code detected in document. User blocked."
        
        # Limitation Fix: Audit Logging
        log_event(user["sub"], "UPLOAD_THREAT", f"Type: {threat_type} | File: {file.filename}", status="BLOCKED")
        return {"error": msg}

    # 🧹 Sanitization
    clean = sanitize(content)

    # 🔍 PII Detection
    pii = detect_pii(clean)

    # 🔐 Pseudonymization
    pseudo_text = pseudonymize(clean, pii, owner_id=owner_id)

    # Store
    try:
        store(pseudo_text, owner_id)
        log_event(user["sub"], "DOCUMENT_UPLOAD", f"File: {file.filename} securely embedded.")
    except Exception as e:
        err = str(e)
        if "quota" in err or "429" in err or "RateLimit" in err:
            return {"error": "⚠️ Gemini API quota exceeded. Please try again later."}
        return {"error": f"Storage failed: {err}"}

    return {
        "msg": "Stored Securely",
        "pii_detected": pii,
        "pseudo_preview": pseudo_text[:200]
    }

@app.post("/query")
def query(q: str, token: str):
    user = authorize(token)
    
    # Limitation Fix: DoS Protection via Rate Limiter
    check_rate_limit(user["sub"])

    is_threat, threat_type = detect_threat(q)
    if is_threat:
        if user["sub"] != "admin": # LIMITATION FIX: Master admin immunity
            block_user(user["sub"])
            
        msg = "🔴 Prompt injection attempt detected. User blocked." if threat_type == "prompt_injection" else "🔴 Malicious query detected. User blocked."
        
        log_event(user["sub"], "QUERY_THREAT", f"Type: {threat_type} | Query: {q[:50]}...", status="BLOCKED")
        return {"answer": msg, "source": ""}

    # 🏦 Banking topic filter — keyword-based, reliable
    if not is_banking_query(q):
        return {
            "answer": "⚠️ I can only assist with banking and financial topics. Please ask a banking-related question.",
            "source": ""
        }

    owner_ids = ["admin"]
    if user.get("role") != "admin":
        owner_ids.append(user["sub"])

    try:
        context = retrieve(q, owner_ids)
        safe_context = [sanitize(c) for c in context]
        ans, source = generate(q, safe_context)
    except Exception as e:
        err = str(e)
        if "quota" in err or "429" in err or "RateLimit" in err:
            return {"answer": "⚠️ API quota exceeded. Please try again later.", "source": ""}
        return {"answer": f"Error processing query: {err}", "source": ""}

    return {"answer": ans, "source": source}

@app.get("/audits")
def get_audits(token: str):
    user = authorize(token)
    # Limitation Fix: Only Master Admin can see audits
    if user.get("sub") != "admin":
        return {"error": "Unauthorized: Master Admin only"}
    
    # Fetch exactly the 50 latest audits
    logs = list(get_audit_collection().find({}, {"_id": 0}).sort("timestamp", -1).limit(50))
    return {"audits": logs}

# --- MASTER ADMIN: USER MANAGEMENT ---

@app.get("/users")
def get_users(token: str):
    user = authorize(token)
    if user.get("sub") != "admin":
        return {"error": "Unauthorized: Master Admin only"}
    
    # Filter out blocked users from the management dashboard
    users = list(get_users_collection().find({"is_blocked": {"$ne": True}}, {"_id": 0, "password": 0}))
    return {"users": users}

@app.post("/users/{target_username}/promote")
def promote_user(target_username: str, token: str):
    user = authorize(token)
    if user.get("sub") != "admin":
        return {"error": "Unauthorized: Master Admin only"}
    
    result = get_users_collection().update_one(
        {"username": target_username},
        {"$set": {"role": "admin"}}
    )
    
    if result.modified_count > 0:
        log_event(user["sub"], "USER_PROMOTED", f"Elevated {target_username} to general admin.")
        return {"msg": f"User {target_username} promoted to admin successfully."}
    return {"error": "User not found or already an admin."}

@app.post("/users/{target_username}/demote")
def demote_user(target_username: str, token: str):
    user = authorize(token)
    if user.get("sub") != "admin":
        return {"error": "Unauthorized: Master Admin only"}
        
    if target_username == "admin":
        return {"error": "Cannot demote the Master Admin."}
    
    result = get_users_collection().update_one(
        {"username": target_username},
        {"$set": {"role": "user"}}
    )
    
    if result.modified_count > 0:
        log_event(user["sub"], "USER_DEMOTED", f"Demoted {target_username} to basic user.")
        return {"msg": f"User {target_username} demoted to user successfully."}
    return {"error": "User not found or already a basic user."}