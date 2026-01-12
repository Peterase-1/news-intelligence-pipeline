
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.databases.postgres.db_manager import init_db
from minio import Minio

def init_minio():
    print("🌊 Connecting to MinIO at localhost:9000...")
    client = Minio(
        "localhost:9000",
        access_key="minio_user",
        secret_key="minio_password",
        secure=False
    )
    
    bucket_name = "news-data-lake"
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"✅ Created bucket: {bucket_name}")
    else:
        print(f"✅ Bucket '{bucket_name}' already exists.")

if __name__ == "__main__":
    print("🚀 Initializing Storage Layer...")
    init_db()
    
    try:
        init_minio()
    except Exception as e:
        print(f"❌ MinIO Error: {e}")
