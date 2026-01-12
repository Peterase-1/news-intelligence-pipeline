
import sys
import os
import pandas as pd
from minio import Minio
from sqlalchemy import create_engine, text

# Specs
POSTGRES_URL = "postgresql://user:password@localhost:5433/news_db"
MINIO_URL = "localhost:9000"
MINIO_ACCESS = "minio_user"
MINIO_SECRET = "minio_password"

def check_postgres():
    print("\n🐘 Checking Postgres...")
    try:
        engine = create_engine(POSTGRES_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM news_articles"))
            count = result.scalar()
            print(f"   -> Found {count} articles in 'news_articles' table.")
            
            if count > 0:
                print("   -> Sample Data:")
                df = pd.read_sql("SELECT * FROM news_articles ORDER BY created_at DESC LIMIT 3", conn)
                print(df[["title", "source", "updated_at"]].to_string())
    except Exception as e:
        print(f"❌ Postgres Error: {e}")

def check_minio():
    print("\n🌊 Checking MinIO (Data Lake)...")
    try:
        client = Minio(MINIO_URL, access_key=MINIO_ACCESS, secret_key=MINIO_SECRET, secure=False)
        objects = client.list_objects("news-data-lake", recursive=True)
        count = 0
        for obj in objects:
            count += 1
            if count <= 5:
                print(f"   -> Found File: {obj.object_name} ({obj.size} bytes)")
        
        if count == 0:
            print("   -> Bucket 'news-data-lake' is empty.")
        else:
            print(f"   -> Total Objects: {count}")
            
    except Exception as e:
        print(f"❌ MinIO Error: {e}")

if __name__ == "__main__":
    check_postgres()
    check_minio()
