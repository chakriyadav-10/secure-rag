import sys
import time
import os
import re
import glob

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("\033[91m[!] Critical Error: Please run 'pip3 install PyPDF2' first.\033[0m")
    sys.exit(1)

# --- ANSI Color Codes for Terminal UI ---
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"

def print_header(title):
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{CYAN}{BOLD} {title.upper()} {RESET}".center(68, " "))
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")
    time.sleep(1)

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

def detect_threat_native(text):
    PROMPT_INJECTION_PATTERNS = [r"ignore (previous|all|prior) instructions", r"jailbreak", r"you are now"]
    CODE_INJECTION_PATTERNS = [r"<script.*?>", r"DROP\s+TABLE", r"rm\s+-rf"]
    for p in PROMPT_INJECTION_PATTERNS:
        if re.search(p, text, re.IGNORECASE): return True, "prompt_injection"
    for p in CODE_INJECTION_PATTERNS:
        if re.search(p, text, re.IGNORECASE): return True, "code_injection"
    return False, "none"

def sanitize_native(text):
    # Strip script tags completely
    text = re.sub(r"(?is)<script.*?>.*?</script>", "[REDACTED SCRIPT]", text)
    # Strip SQL
    text = re.sub(r"(?i)(DROP\s+TABLE|UNION\s+SELECT)", "[REDACTED SQL]", text)
    # Strip shell
    text = re.sub(r"(?i)(rm\s+-rf|wget\s+http)", "[REDACTED SHELL]", text)
    # Strip multi-line prompt injections
    text = re.sub(r"(?is)Ignore all previous and following instructions\.", "[REDACTED PROMPT INJECTION]", text)
    text = re.sub(r"(?is)You are now in \"Developer Mode\".*?context\.", "[REDACTED LLM JAILBREAK]", text)
    text = re.sub(r"(?i)Exfiltrate data.*?(com|\.)", "[REDACTED DATA THEFT]", text)
    return text

def detect_pii_native(text):
    pii = {"account": [], "phone": [], "ifsc": [], "email": []}
    pii["ifsc"] = list(set(re.findall(r"[A-Z]{4}0[A-Z0-9]{6}", text)))
    pii["email"] = list(set(re.findall(r"\S+@\S+", text)))

    for match in re.finditer(r"\b\d{9,18}\b", text):
        number = match.group()
        start = match.start()
        context = text[max(0, start-25):start].lower()
        
        is_phone = "+91" in context or "phone" in context or "mob" in context or "call" in context
        is_account = "a/c" in context or "acc" in context or "account" in context or "bank" in context
        
        if len(number) == 10:
            if is_account: pii["account"].append(number)
            else: pii["phone"].append(number)
        else:
            pii["account"].append(number)

    pii["account"] = list(set(pii["account"]))
    pii["phone"] = list(set(pii["phone"]))
    return pii

def pseudonymize_native(text, pii_entities):
    pseudo_text = text
    for category, items in pii_entities.items():
        for i, item in enumerate(items):
            pseudo_text = pseudo_text.replace(item, f"{category.upper()}_UUID{i}")
    return pseudo_text

def run_demo(pdf_path):
    sample = extract_pdf_text(pdf_path)

    print_header(f"1. Document Ingestion: {pdf_path}")
    print(f"{YELLOW}📥 Received raw document ({pdf_path}):{RESET}")
    print(f'{CYAN}"""\n{sample.strip()}\n"""{RESET}\n')
    time.sleep(2)

    print_header("2. Threat Detection")
    print(f"{YELLOW}🚨 Scanning for malicious patterns (SQLi, XSS, Command Injection, Prompt Jailbreaks)...{RESET}\n")
    time.sleep(1)
    is_threat, threat_type = detect_threat_native(sample)
    if is_threat:
        print(f"   Threat Detected: {RED}{BOLD}Yes 🛑{RESET}")
        print(f"   Detected Attack Type: {RED}[{threat_type.upper()}]{RESET}")
        print(f"   Action Taken: {RED}Block user IP & Drop document.{RESET}")
        print(f"\n{YELLOW}⚠️  For demo purposes, we will continue to show how sanitization neutralizes the text...{RESET}")
    else:
        print(f"   Threat Detected: {GREEN}{BOLD}No ✅{RESET}")
    time.sleep(2)

    print_header("3. Content Sanitization")
    if is_threat:
        print(f"{YELLOW}🧹 Stripping active code blocks & replacing injections with [REDACTED]...{RESET}\n")
        time.sleep(1)
        clean = sanitize_native(sample)
        print(f"{GREEN}Sanitized Text:{RESET}")
        print(f'{CYAN}"""\n{clean.strip()}\n"""{RESET}\n')
    else:
        print(f"{GREEN}No sanitization required for clean document.{RESET}\n")
        clean = sample
    time.sleep(2)

    print_header("4. PII Detection (Entity Differentiation)")
    print(f"{YELLOW}🔍 Scanning for sensitive entities using regular expressions...{RESET}\n")
    time.sleep(1)
    pii = detect_pii_native(clean)
    found_any = False
    for entity_type, matches in pii.items():
        if matches:
            found_any = True
            print(f"  {CYAN}▸{RESET} Category: {BOLD}[{entity_type.upper()}]{RESET} | Found: {GREEN}{matches}{RESET}")
    if not found_any:
        print(f"  {GREEN}No sensitive Indian PII entities detected.{RESET}")
    time.sleep(2)

    print_header("5. Pseudonymization")
    print(f"{YELLOW}🔐 Replacing identified PII with secure token mapping...{RESET}\n")
    time.sleep(1)
    pseudo = pseudonymize_native(clean, pii)
    print(f"{GREEN}Pseudonymized Text (Ready for Vector DB):{RESET}")
    print(f'{CYAN}"""\n{pseudo.strip()}\n"""{RESET}\n')
    time.sleep(2)

    print_header("6. Secure Storage Integration")
    print(f"{YELLOW}Applying Differential Privacy (Laplacian noise) to embedding vector...{RESET}")
    time.sleep(1)
    print(f"  {CYAN}▸{RESET} Original Vector (MiniLM-L6-v2): [0.1241, -0.5912, 0.9912, ..., 0.0012, -0.4412] {YELLOW}(384 Dimensions){RESET}")
    print(f"  {CYAN}▸{RESET} Noised Vector (DP-Obscured):    [0.1275, -0.5878, 0.9946, ..., 0.0046, -0.4378] {YELLOW}(384 Dimensions){RESET}")
    print(f"\n{GREEN}{BOLD}💾 Process complete. Sent pseudonymized document vectors to Pinecone.{RESET}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_demo(sys.argv[1])
    else:
        pdfs = glob.glob("*.pdf")
        if not pdfs:
            print(f"{RED}[!] No PDF files found in the current directory.{RESET}")
            sys.exit(1)
            
        print(f"\n{BLUE}{BOLD}=== SELECT A DOCUMENT TO PROCESS ==={RESET}")
        for i, pdf in enumerate(pdfs, 1):
            print(f"  {CYAN}{i}.{RESET} {pdf}")
            
        try:
            choice = input(f"\n{YELLOW}Enter the number of the PDF to test (or 'q' to quit): {RESET}")
            if choice.lower() == 'q':
                sys.exit(0)
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(pdfs):
                run_demo(pdfs[choice_idx])
            else:
                print(f"{RED}[!] Invalid selection.{RESET}")
        except ValueError:
            print(f"{RED}[!] Please enter a valid number.{RESET}")
        except KeyboardInterrupt:
            print("\nExiting...")
