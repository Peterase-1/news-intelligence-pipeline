
from sqlalchemy import create_engine
from sqlalchemy import text

# Try connecting as 'postgres' superuser
DATABASE_URL = "postgresql://postgres:password@127.0.0.1:5432/news_db"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ Success connection as 'postgres' user!")
except Exception as e:
    print(f"❌ Failed as 'postgres': {e}")
