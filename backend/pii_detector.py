import re

def detect_pii(text):
    pii = {"account": [], "phone": [], "ifsc": [], "email": []}
    
    # Static distinct patterns
    pii["ifsc"] = list(set(re.findall(r"[A-Z]{4}0[A-Z0-9]{6}", text)))
    pii["email"] = list(set(re.findall(r"\S+@\S+", text)))

    # Find all 9-18 digit numbers (Candidates for Account or Phone)
    # We find their start index to look at the preceding context
    for match in re.finditer(r"\b\d{9,18}\b", text):
        number = match.group()
        start = match.start()
        
        # Look at the 25 characters before the number for context clues
        context = text[max(0, start-25):start].lower()
        
        is_phone = False
        is_account = False
        
        if "+91" in context or "phone" in context or "mob" in context or "call" in context:
            is_phone = True
        elif "a/c" in context or "acc" in context or "account" in context or "bank" in context:
            is_account = True
        
        # If it's 10 digits in India, default to Phone unless context says Account
        if len(number) == 10:
            if is_account:
                pii["account"].append(number)
            else:
                pii["phone"].append(number)
        else:
            # Not 10 digits = definitely a bank account, not a standard Indian phone
            pii["account"].append(number)

    # Clean duplicates
    pii["account"] = list(set(pii["account"]))
    pii["phone"] = list(set(pii["phone"]))

    return pii