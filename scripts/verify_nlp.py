
from sqlalchemy import create_engine
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage.databases.postgres.db_manager import DATABASE_URL

def verify_nlp():
    print("🧠 Checking NLP Results in DB...")
    engine = create_engine(DATABASE_URL)
    
    query = """
    SELECT 
        title, 
        substring(source for 10) as source,
        sentiment_label, 
        sentiment_score,
        length(embedding) as embed_len
    FROM news_articles
    WHERE sentiment_label IS NOT NULL
    LIMIT 5;
    """
    
    df = pd.read_sql(query, engine)
    print(df.to_string())

if __name__ == "__main__":
    verify_nlp()
