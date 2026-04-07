import os
import sys
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

# Ensure we can import from the backend directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("❌ Error: MONGO_URI not found in .env file.")
    sys.exit(1)

def unblock_all():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client["secure_rag_db"]
        users_col = db["users"]
        
        # Count blocked users before
        count_before = users_col.count_documents({"is_blocked": True})
        if count_before == 0:
            print("✅ No blocked users found in the database. Everything is already clear.")
            return

        print(f"📦 Found {count_before} blocked accounts. Resetting access permissions...")
        
        # Perform the update
        result = users_col.update_many(
            {"is_blocked": True},
            {"$set": {"is_blocked": False}}
        )
        
        print(f"✨ Successfully unblocked {result.modified_count} users.")
        print("🚀 You can now re-test the live website with these accounts.")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    unblock_all()
