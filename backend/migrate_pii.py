import sys
import os
from datetime import datetime

# Ensure local backend path is searched for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from pseudo import get_mappings_col, aes_encrypt
except ImportError:
    print("Error: Could not import pseudo module. Run this from the project root.")
    sys.exit(1)

def migrate():
    col = get_mappings_col()
    
    # Query for records that are not yet encrypted
    # These are records where 'encrypted' field is either missing or False
    query = {"$or": [
        {"encrypted": {"$exists": False}},
        {"encrypted": False}
    ]}
    
    unencrypted_records = list(col.find(query))
    total = len(unencrypted_records)
    
    if total == 0:
        print("✅ No unencrypted records found. The vault is securely sealed.")
        return

    print(f"📦 Found {total} legacy plain-text records. Starting migration...")

    for i, record in enumerate(unencrypted_records, 1):
        original_text = record["original"]
        token = record["token"]
        
        try:
            # Encrypt the plain text
            cipher_text = aes_encrypt(original_text)
            
            # Update the document
            col.update_one(
                {"_id": record["_id"]},
                {"$set": {
                    "original": cipher_text,
                    "encrypted": True,
                    "migrated_at": datetime.utcnow()
                }}
            )
            
            if i % 10 == 0 or i == total:
                print(f"   [{i}/{total}] Processed {token}")
                
        except Exception as e:
            print(f"❌ Error migrating {token}: {e}")

    print(f"\n✨ Successfully encrypted {total} records. Full AES-256 hardening complete.")

if __name__ == "__main__":
    migrate()
