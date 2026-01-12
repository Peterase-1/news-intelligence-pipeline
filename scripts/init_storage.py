
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.databases.postgres.db_manager import init_db

if __name__ == "__main__":
    print("🚀 Initializing Storage Layer...")
    init_db()
