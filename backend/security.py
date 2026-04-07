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
    r"\bignore (?:previous|all|prior|your) instructions\b",
    r"\bdisregard (?:previous|all|prior|your) instructions\b",
    r"\bforget (?:previous|all|prior|your) instructions\b",
    r"\byou are now (?:a|an|in|the|your) (?:helpful|assistant|developer|hacker|bot|terminal|linux|DAN|master|system)\b",
    r"\bact as (?:a|an|if) (?:helpful|assistant|developer|hacker|bot|terminal|linux|DAN|master|system)\b",
    r"\bpretend (?:you are|to be|that) (?:someone|a|an|the|your) (?:else|assistant|developer|hacker|bot|terminal|linux)\b",
    r"\breveal (?:your|the) (?:system|hidden|prompt|secret|confidential) (?:instruction|context|data)\b",
    r"\bprint (?:all|every|the full) (?:system|hidden|prompt) (?:context|document|data|instruction)\b",
    r"\brepeat (?:everything|all|the above|your instructions)\b",
    r"\bjailbreak\b",
    r"\bDAN mode\b",
    r"\bdeveloper mode\b",
    r"\bbypass (?:security|filter|restriction|rule)\b",
    r"\bnew instruction\b",
    r"\boverride (?:instruction|rule|system|setting)\b",
    r"\bexfiltrate\b",
    r"\bsend (?:to|data to|results to) (?:http|https|ftp|attacker|external)\b",
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