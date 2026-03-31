import time
from fastapi import HTTPException

# In-Memory Token Bucket for Demo Purposes
# (In production, this would be Redis to sync across server instances)
user_requests = {}
MAX_REQUESTS_PER_MINUTE = 15

def check_rate_limit(username: str):
    """
    LIMITATION FIX: Strict Banking Rate-Limiting & Session Timeouts
    Enforces Strict API Rate Limiting to prevent DoS attacks on the LLM quota.
    """
    current_time = time.time()
    
    if username not in user_requests:
        user_requests[username] = []
        
    # Clean up requests older than 60 seconds
    user_requests[username] = [t for t in user_requests[username] if current_time - t < 60]
    
    # Check threshold
    if len(user_requests[username]) >= MAX_REQUESTS_PER_MINUTE:
        print(f"🛑 [RATE LIMIT EXCEEDED] User '{username}' blocked for 60 seconds.")
        raise HTTPException(status_code=429, detail="Banking Security: API Quota Exceeded. Please try again in 60 seconds.")
        
    # Log the valid request
    user_requests[username].append(current_time)
