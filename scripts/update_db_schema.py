
import sys
import os
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage.databases.postgres.db_manager import DATABASE_URL

def migrate_schema():
    print("🔄 Migrating Database Schema...")
    engine = create_engine(DATABASE_URL)
    
    commands = [
        "ALTER TABLE news_articles ADD COLUMN IF NOT EXISTS sentiment_score INTEGER;",
        "ALTER TABLE news_articles ADD COLUMN IF NOT EXISTS sentiment_label VARCHAR;",
        "ALTER TABLE news_articles ADD COLUMN IF NOT EXISTS embedding TEXT;"
    ]
    
    with engine.connect() as conn:
        for cmd in commands:
            try:
                conn.execute(text(cmd))
                conn.commit()
                print(f"   ✅ Executed: {cmd}")
            except Exception as e:
                print(f"   ⚠️ Error (might already exist): {e}")
    
    print("✨ Schema Migration Complete.")

if __name__ == "__main__":
    migrate_schema()
