
import sys
import os
import json
import psycopg2
from pyspark.sql.functions import from_json, col, current_timestamp, struct, to_json
from pyspark.sql.types import StructType, StructField, StringType

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from processing.spark.utils.spark_session import get_spark_session
from processing.spark.jobs.clean_news import clean_text_udf

# Define Schema
news_schema = StructType([
    StructField("url", StringType(), True),
    StructField("source", StringType(), True),
    StructField("title", StringType(), True),
    StructField("body", StringType(), True),
    StructField("author", StringType(), True),
    StructField("published_at", StringType(), True),
    StructField("scraped_at", StringType(), True)
])

def configure_hadoop_s3(spark):
    """Configures Spark to talk to MinIO (S3)"""
    sc = spark.sparkContext
    sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", "http://minio:9000")
    sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", "minio_user")
    sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "minio_password")
    sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
    sc._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

def write_to_postgres(rows):
    """
    Writes a list of Row objects to Postgres using psycopg2 with ON CONFLICT handling.
    """
    if not rows:
        return

    try:
        # Connect to Postgres (Internal Docker Name)
        conn = psycopg2.connect(
            host="postgres",
            port="5432",
            database="news_db",
            user="user",
            password="password"
        )
        cur = conn.cursor()
        
        insert_query = """
            INSERT INTO news_articles (url, source, title, author, published_at, scraped_at, body_text, updated_at, is_processed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING;
        """
        
        data_tuples = [
            (
                r.url, 
                r.source, 
                r.title, 
                r.author, 
                r.published_at, 
                r.scraped_at, 
                r.body_text, 
                r.updated_at,
                True # is_processed
            ) 
            for r in rows
        ]
        
        cur.executemany(insert_query, data_tuples)
        conn.commit()
        print(f"   ✅ Postgres: Inserted/Ignored {len(rows)} records.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ CSV/DB Error: {e}")

def process_batch(df, epoch_id):
    """
    Writes the batch to multiple sinks.
    """
    print(f"📦 Processing Batch {epoch_id} with {df.count()} records...")
    
    if df.count() == 0:
        return

    # --- 1. Write to Data Lake (MinIO) ---
    try:
        s3_path = "s3a://news-data-lake/silver/news_articles"
        df.write \
            .format("parquet") \
            .mode("append") \
            .save(s3_path)
        print("   ✅ MinIO: Written Parquet.")
    except Exception as e:
        print(f"   ❌ MinIO Error: {e}")

    # --- 2. Write to Database (Postgres) ---
    try:
        # Prepare data for Postgres (select columns)
        postgres_df = df.select(
            col("url"),
            col("source"),
            col("title"),
            col("author"),
            col("published_at").cast("timestamp"),
            col("scraped_at").cast("timestamp"),
            col("body_cleaned").alias("body_text"),
            col("processed_at").alias("updated_at")
        )
        
        # Collect to driver and insert via psycopg2
        rows = postgres_df.collect()
        write_to_postgres(rows)
        
    except Exception as e:
        print(f"   ❌ Postgres Batch Error: {e}")

def run_streaming_job():
    spark = get_spark_session("NewsProcessor")
    spark.sparkContext.setLogLevel("WARN")

    configure_hadoop_s3(spark)

    print("🚀 Starting Spark Storage Integration Job...")

    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
    
    # 1. Read Stream
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", bootstrap_servers) \
        .option("subscribe", "raw_news_topic") \
        .option("startingOffsets", "earliest") \
        .load()

    # 2. Parse & Clean
    json_df = df.select(from_json(col("value").cast("string"), news_schema).alias("data")).select("data.*")
    
    cleaned_df = json_df.withColumn("body_cleaned", clean_text_udf(col("body"))) \
                        .withColumn("processed_at", current_timestamp())

    # 3. Write Stream (ForeachBatch)
    query = cleaned_df.writeStream \
        .foreachBatch(process_batch) \
        .option("checkpointLocation", "/tmp/checkpoint_storage_v2") \
        .start()

    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    run_streaming_job()
