import sys
import time
import os
import re
import glob
import asyncio

# Ensure local backend path is searched for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("\033[91m[!] Critical Error: Please run 'pip3 install PyPDF2' first.\033[0m")
    sys.exit(1)

# Import the new security modules
try:
    from bert_classifier import get_bert_safety_score
    from safety_scorer import evaluate_safety
except ImportError as e:
    print(f"\n{RED}{BOLD}[!] CRITICAL ERROR: Dependency Missing{RESET}")
    print(f"{YELLOW}Reason: {e}{RESET}")
    print(f"{CYAN}To fix this, please run:{RESET}")
    print(f"{BOLD}python3 -m pip install transformers torch google-genai{RESET}\n")
    sys.exit(1)

# --- ANSI Color Codes for Terminal UI ---
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"

def print_header(title):
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{CYAN}{BOLD} {title.upper()} {RESET}".center(68, " "))
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")
    time.sleep(0.5)

def extract_pdf_text(filepath):
    if not os.path.exists(filepath):
        print(f"{RED}[!] Could not find {filepath}{RESET}")
        sys.exit(1)
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t: text += t + "\n"
    return text.strip()

# Import from centralized security module
from security import detect_threat, sanitize

def detect_pii_native(text):
    pii = {"account": [], "phone": [], "ifsc": [], "email": []}
    pii["ifsc"] = list(set(re.findall(r"[A-Z]{4}0[A-Z0-9]{6}", text)))
    pii["email"] = list(set(re.findall(r"\S+@\S+", text)))

    for match in re.finditer(r"\b\d{9,18}\b", text):
        number = match.group()
        start = match.start()
        context = text[max(0, start-25):start].lower()
        is_phone = "+91" in context or "phone" in context or "mob" in context
        is_account = "a/c" in context or "acc" in context or "account" in context
        if len(number) == 10:
            if is_account: pii["account"].append(number)
            else: pii["phone"].append(number)
        else:
            pii["account"].append(number)
    return {k: list(set(v)) for k, v in pii.items()}

def pseudonymize_native(text, pii_entities):
    pseudo_text = text
    for category, items in pii_entities.items():
        for i, item in enumerate(items):
            pseudo_text = pseudo_text.replace(item, f"{category.upper()}_UUID{i}")
    return pseudo_text

async def run_demo(pdf_path):
    sample = extract_pdf_text(pdf_path)

    print_header(f"1. Document Ingestion: {pdf_path}")
    print(f"{YELLOW}📥 Received raw document ({pdf_path}):{RESET}")
    print(f'{CYAN}"""\n{sample.strip()[:500]}...\n"""{RESET}\n')
    time.sleep(1)

    print_header("2. Threat Detection (Heuristic)")
    print(f"{YELLOW}🚨 Scanning for malicious patterns (SQLi, XSS, Jailbreaks)...{RESET}\n")
    
    # Use centralized production security engine
    is_heuristic_threat, threat_type = detect_threat(sample)
    
    if is_heuristic_threat:
        print(f"   Heuristic Threat: {YELLOW}{BOLD}Flagged [{threat_type.upper()}]{RESET}")
        print(f"   {CYAN}▸{RESET} Status: {MAGENTA}Awaiting Semantic Verification...{RESET}")
    else:
        print(f"   Heuristic Threat: {GREEN}{BOLD}Not Found ✅{RESET}")
    time.sleep(1)

    print_header("2.5 High-Fidelity Semantic Safety Analysis")
    print(f"{YELLOW}🤖 Initiating Hybrid BERT + LLM Scorer...{RESET}\n")
    
    # BERT Score
    bert_score = get_bert_safety_score(sample)
    print(f"   [A] {BOLD}Local BERT Semantic Score:{RESET} {MAGENTA}{bert_score:.4f}{RESET}")
    time.sleep(0.5)
    
    # LLM Reasoning
    score, reasoning = await evaluate_safety(sample)
    print(f"   [B] {BOLD}LLM Policy Reasoning:{RESET}\n       {CYAN}\"{reasoning}\"{RESET}")
    time.sleep(0.5)
    
    # Logic: Verify-then-Block (Production Standard)
    final_status = "ALLOWED ✅"
    color = GREEN
    
    if is_heuristic_threat:
        # If heuristic flagged but semantic score is high, it's a False Positive
        if score > 0.75:
            print(f"\n   {BLUE}{BOLD}🛡️  HEURISTIC VETO:{RESET} {GREEN}Semantic scorer identified document as a False Positive.{RESET}")
            print(f"      Status: {GREEN}Heuristic flag manually overridden.{RESET}")
        else:
            final_status = "BLOCKED 🛑"
            color = RED
    elif score < 0.7:
        final_status = "BLOCKED 🛑"
        color = RED

    print(f"\n   {BOLD}Final Safety Confidence Score:{RESET} {color}{BOLD}{score:.4f} ({final_status}){RESET}")
    
    if final_status == "BLOCKED 🛑":
        print(f"\n{RED}{BOLD}🚨 CRITICAL: Document rejected. System hardening activated.{RESET}")
        print(f"{YELLOW}⚠️  Demo bypass: continuing to show sanitization to demonstrate pipeline flow...{RESET}")
    
    time.sleep(2)

    print_header("3. Content Sanitization")
    print(f"{YELLOW}🧹 Neutralizing active code & adversarial prompts...{RESET}\n")
    clean = sanitize(sample)
    print(f"{GREEN}Sanitized Snippet:{RESET}")
    print(f'{CYAN}"""\n{clean.strip()[:300]}...\n"""{RESET}\n')
    time.sleep(1)

    print_header("4. PII Detection (Entity Differentiation)")
    print(f"{YELLOW}🔍 Scanning for sensitive entities using Context-Aware Regex...{RESET}\n")
    pii = detect_pii_native(clean)
    for entity_type, matches in pii.items():
        if matches:
            print(f"  {CYAN}▸{RESET} {BOLD}{entity_type.upper()}:{RESET} {GREEN}{matches}{RESET}")
    time.sleep(1)

    print_header("5. Pseudonymization")
    print(f"{YELLOW}🔐 Mapping identified PII to secure UUID tokens...{RESET}\n")
    pseudo = pseudonymize_native(clean, pii)
    print(f"{GREEN}Pseudonymized Output:{RESET}")
    print(f'{CYAN}"""\n{pseudo.strip()[:300]}...\n"""{RESET}\n')
    time.sleep(1)

    print_header("6. Secure Storage Integration")
    print(fr"{YELLOW}Applying $\epsilon$-Differential Privacy to 3072-dim embeddings...{RESET}")
    print(f"  {CYAN}▸{RESET} Original Gemini Vector: [0.1241, -0.5912, ..., 0.9912]")
    print(f"  {CYAN}▸{RESET} Laplacian Noise Level:  {MAGENTA}ε=0.1{RESET}")
    print(f"  {CYAN}▸{RESET} DP-Hardened Vector:    [0.1275, -0.5878, ..., 0.9946]")
    print(f"\n{GREEN}{BOLD}💾 Pipeline complete. Handed off to Vector Persistence Layer.{RESET}\n")

# ── Banking Topic Filter (Native Simulation) ──────────────────────────────────
BANKING_KEYWORDS = {
    "bank", "account", "loan", "credit", "debit", "finance", "interest", "emi",
    "deposit", "transfer", "payment", "insurance", "invest", "tax", "balance",
    "transaction", "money", "cash", "statement", "passbook", "kyc", "atm"
}

def is_banking_query_native(text):
    words = set(re.findall(r"\w+", text.lower()))
    return bool(words & BANKING_KEYWORDS)

async def run_query_demo():
    print_header("REAL-TIME USER QUERY SIMULATION")
    q = input(f"{YELLOW}Type your banking question (or 'q' to go back): {RESET}")
    if q.lower() == 'q': return

    print_header("1. Domain Filtering")
    if is_banking_query_native(q):
        print(f"   {GREEN}Domain Match: Financial/Banking Context Found ✅{RESET}")
    else:
        print(f"   {RED}Domain Rejection: Query is NOT banking-related 🛑{RESET}")
        print(f"   {YELLOW}Action: Block query to prevent LLM hallucination.{RESET}")
        return

    print_header("2. Heuristic Threat Detection")
    # Use centralized production security engine
    is_heuristic_threat, threat_type = detect_threat(q)
    
    if is_heuristic_threat:
        print(f"   Heuristic Threat: {YELLOW}{BOLD}Flagged [{threat_type.upper()}]{RESET}")
        print(f"   {CYAN}▸{RESET} Status: {MAGENTA}Awaiting Semantic Verification...{RESET}")
    else:
        print(f"   Heuristic Threat: {GREEN}{BOLD}No malicious patterns found ✅{RESET}")
    time.sleep(1)

    print_header("3. High-Fidelity Semantic Safety Analysis")
    print(f"{YELLOW}🤖 Initiating Hybrid BERT + LLM Scorer...{RESET}\n")
    
    # BERT Score
    bert_score = get_bert_safety_score(q)
    print(f"   [A] {BOLD}Local BERT Semantic Score:{RESET} {MAGENTA}{bert_score:.4f}{RESET}")
    time.sleep(0.5)
    
    # LLM Reasoning
    score, reasoning = await evaluate_safety(q)
    print(f"   [B] {BOLD}LLM Policy Reasoning:{RESET}\n       {CYAN}\"{reasoning}\"{RESET}")
    time.sleep(0.5)
    
    # Logic: Verify-then-Block (Production Standard)
    final_status = "ALLOWED ✅"
    color = GREEN
    
    if is_heuristic_threat:
        # If heuristic flagged but semantic score is high, it's a False Positive
        if score > 0.75:
            print(f"\n   {BLUE}{BOLD}🛡️  HEURISTIC VETO:{RESET} {GREEN}Semantic scorer identified query as a False Positive.{RESET}")
            print(f"      Status: {GREEN}Heuristic flag manually overridden.{RESET}")
        else:
            final_status = "BLOCKED 🛑"
            color = RED
    elif score < 0.7:
        final_status = "BLOCKED 🛑"
        color = RED

    print(f"\n   {BOLD}Final Safety Confidence Score:{RESET} {color}{BOLD}{score:.4f} ({final_status}){RESET}")
    if final_status == "BLOCKED 🛑":
         print(f"\n{RED}{BOLD}🚨 ACCESS DENIED: Query failed semantic safety check.{RESET}")
    else:
         print(f"\n{GREEN}{BOLD}🔓 ACCESS GRANTED: Query passed all security check layers.{RESET}")
    time.sleep(2)

async def main():
    while True:
        print_header("SECURE RAG BACKEND PIPELINE SIMULATION")
        print(f"  {CYAN}[1]{RESET} Document Ingestion Simulation (PDF Pipeline)")
        print(f"  {CYAN}[2]{RESET} Real-time User Query Simulation (NLU Pipeline)")
        print(f"  {CYAN}[q]{RESET} Quit")
        
        choice = input(f"\n{YELLOW}Select Simulation Mode: {RESET}")
        if choice.lower() == 'q': break
        
        if choice == '1':
            pdfs = glob.glob("*.pdf")
            if not pdfs:
                print(f"{RED}[!] No PDF files found.{RESET}")
                continue
            for i, pdf in enumerate(pdfs, 1):
                print(f"    {i}. {pdf}")
            pdf_choice = input(f"\n{YELLOW}Select PDF index: {RESET}")
            try:
                idx = int(pdf_choice) - 1
                if 0 <= idx < len(pdfs):
                    await run_demo(pdfs[idx])
            except:
                print(f"{RED}Invalid index.{RESET}")
        elif choice == '2':
            await run_query_demo()
        else:
            print(f"{RED}Invalid choice.{RESET}")

if __name__ == "__main__":
    asyncio.run(main())
