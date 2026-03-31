import re

# ── Code/Command Injection Patterns ──────────────────────────────────────────
CODE_INJECTION_PATTERNS = [
    r"<script.*?>",           # XSS
    r"DROP\s+TABLE",          # SQL
    r"UNION\s+SELECT",        # SQL
    r"rm\s+-rf",              # Shell
    r"system\(",              # Shell
    r"exec\(",                # Shell
    r"__import__",            # Python exec
    r"eval\(",                # Code injection
    r"os\.system",            # Python shell
    r"subprocess",            # Python shell
    r"curl\s+http",           # Remote fetch
    r"wget\s+http",           # Remote fetch
]

# ── Prompt Injection / LLM Jailbreak Patterns ────────────────────────────────
PROMPT_INJECTION_PATTERNS = [
    r"ignore (previous|all|prior) instructions",
    r"disregard (previous|all|prior|your) instructions",
    r"forget (previous|all|prior|your) instructions",
    r"you are now",
    r"act as (a|an|if)",
    r"pretend (you are|to be|that)",
    r"reveal (all|user|private|secret|confidential)",
    r"print (all|every|the full) (context|document|data|instruction)",
    r"repeat (everything|all|the above|your instructions)",
    r"jailbreak",
    r"DAN mode",
    r"developer mode",
    r"bypass (security|filter|restriction|rule)",
    r"new instruction",
    r"override (instruction|rule|system|setting)",
    r"exfiltrate",
    r"send (to|data to|results to) (http|https|ftp|attacker)",
]

def detect_threat(text):
    """Returns (is_threat, threat_type) tuple."""
    for p in CODE_INJECTION_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return True, "code_injection"
    for p in PROMPT_INJECTION_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return True, "prompt_injection"
    return False, None

def sanitize(text):
    """Clean known malicious patterns from content before storing/displaying."""
    text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"(DROP\s+TABLE|UNION\s+SELECT)", "[REDACTED]", text, flags=re.IGNORECASE)
    text = re.sub(r"(rm\s+-rf|os\.system|subprocess|eval\(|exec\()", "[REDACTED]", text, flags=re.IGNORECASE)
    # Strip prompt injection attempts from retrieved context
    for p in PROMPT_INJECTION_PATTERNS:
        text = re.sub(p, "[REDACTED]", text, flags=re.IGNORECASE)
    return text