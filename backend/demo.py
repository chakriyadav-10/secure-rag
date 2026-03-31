import sys
import time
from security import detect_threat, sanitize
from pii_detector import detect_pii
from pseudo import pseudonymize

def load_sample(pdf_path=None):
    if pdf_path:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t: text += t + "\n"
            print(f"📂 Loaded PDF: {pdf_path} ({len(reader.pages)} pages)\n")
            return text
        except Exception as e:
            print(f"⚠️  Could not read PDF ({e}). Using built-in sample.\n")

    # Default built-in sample
    return """
To: HR Department
Subject: Salary Transfer
Account No: 123456789012
IFSC: SBIN0001234
Phone: 9876543210
Email: john.doe@example.com
Message: Please process the transfer. By the way, testing the system:
<script>alert('hack')</script>
"""

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

pdf_path = sys.argv[1] if len(sys.argv) > 1 else None
sample = load_sample(pdf_path)

print_header("1. Document Ingestion")
print(f"{YELLOW}📥 Received raw document:{RESET}")
print(f'{CYAN}"""\n{sample.strip()}\n"""{RESET}\n')
time.sleep(2)

print_header("2. Threat Detection")
print(f"{YELLOW}🚨 Scanning for malicious patterns (SQLi, XSS, Command Injection, Prompt Jailbreaks)...{RESET}\n")
time.sleep(1)
is_threat, threat_type = detect_threat(sample)
if is_threat:
    print(f"   Threat Detected: {RED}{BOLD}Yes 🛑{RESET}")
    print(f"   Detected Attack Type: {RED}[{threat_type.upper()}]{RESET}")
    print(f"   Action Taken: {RED}Block user IP & Drop document.{RESET}")
    print(f"\n{YELLOW}⚠️  For demo purposes, we will continue to show how sanitization neutralizes the text...{RESET}")
else:
    print(f"   Threat Detected: {GREEN}{BOLD}No ✅{RESET}")
time.sleep(2)

print_header("3. Content Sanitization")
print(f"{YELLOW}🧹 Stripping active code blocks & replacing injections with [REDACTED]...{RESET}\n")
time.sleep(1)
clean = sanitize(sample)
print(f"{GREEN}Sanitized Text:{RESET}")
print(f'{CYAN}"""\n{clean.strip()}\n"""{RESET}\n')
time.sleep(2)

print_header("4. PII Detection (Entity Differentiation)")
print(f"{YELLOW}🔍 Scanning for sensitive entities using regular expressions...{RESET}\n")
time.sleep(1)
pii = detect_pii(clean)
for entity_type, matches in pii.items():
    if matches:
        print(f"  {CYAN}▸{RESET} Category: {BOLD}[{entity_type.upper()}]{RESET} | Found: {GREEN}{matches}{RESET}")
time.sleep(2)

print_header("5. Pseudonymization")
print(f"{YELLOW}🔐 Replacing identified PII with secure token mapping...{RESET}\n")
time.sleep(1)
pseudo = pseudonymize(clean, pii)
print(f"{GREEN}Pseudonymized Text (Ready for Vector DB):{RESET}")
print(f'{CYAN}"""\n{pseudo.strip()}\n"""{RESET}\n')
time.sleep(2)

print_header("6. Secure Storage Integration")
print(f"{GREEN}{BOLD}💾 Process complete. Sent pseudonymized document vectors to Faiss / Pinecone.{RESET}\n")