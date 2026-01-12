
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from processing.spark.utils.spark_session import get_spark_session
from processing.spark.jobs.clean_news import clean_text_udf
from pyspark.sql.functions import from_json, col, current_timestamp, struct, to_json
from pyspark.sql.types import StructType, StructField, StringType

# Define Schema (must match ingestion/kafka_producer/schema.py)
news_schema = StructType([
    StructField("url", StringType(), True),
    StructField("source", StringType(), True),
    StructField("title", StringType(), True),
    StructField("body", StringType(), True),
    StructField("author", StringType(), True),
    StructField("published_at", StringType(), True),
    StructField("scraped_at", StringType(), True)
])

def run_streaming_job():
    spark = get_spark_session("NewsProcessor")
    spark.sparkContext.setLogLevel("ERROR")

    print("🚀 Starting Spark Streaming Job...")

    # 1. Read from Kafka
    # Use KAFKA_BOOTSTRAP_SERVERS env var if set, otherwise default to "kafka:29092" (Docker network)
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
    
    kafka_options = {
        "kafka.bootstrap.servers": bootstrap_servers,
        "subscribe": "raw_news_topic",
        "startingOffsets": "earliest" # Process missed data
    }
    
    df = spark.readStream \
        .format("kafka") \
        .options(**kafka_options) \
        .load()

    # 2. Parse JSON
    # Kafka value is binary, cast to string then parse
    json_df = df.select(from_json(col("value").cast("string"), news_schema).alias("data")) \
                .select("data.*")

    # 3. Apply Cleaning
    cleaned_df = json_df.withColumn("body_cleaned", clean_text_udf(col("body"))) \
                        .withColumn("processed_at", current_timestamp()) \
                        .drop("body") # Drop raw dirty body if desired
                        
    # 4. Write to Console (Verification)
    query_console = cleaned_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    # 5. Write back to Kafka (Topic: processed_news_topic)
    # Prepare DataFrame for Kafka (key, value)
    kafka_output_df = cleaned_df.select(
        col("url").alias("key"),
        to_json(struct("*")).alias("value")
    )
    
    query_kafka = kafka_output_df.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", bootstrap_servers) \
        .option("topic", "processed_news_topic") \
        .option("checkpointLocation", "/tmp/spark_checkpoint_kafka") \
        .start()

    print("✅ Streaming queries started. Waiting for data...")
    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    run_streaming_job()
