
import json

# Define Avro schema for Raw News
raw_news_schema = {
    "namespace": "news.ingestion",
    "type": "record",
    "name": "RawNewsArticle",
    "fields": [
        {"name": "url", "type": "string"},
        {"name": "source", "type": "string"},
        {"name": "title", "type": "string"},
        {"name": "body", "type": "string"},
        {"name": "author", "type": ["string", "null"]},
        {"name": "published_at", "type": ["string", "null"]},
        {"name": "scraped_at", "type": "string"}
    ]
}

def get_raw_news_schema_str():
    return json.dumps(raw_news_schema)
