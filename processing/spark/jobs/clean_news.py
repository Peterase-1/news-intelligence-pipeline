
import re
from pyspark.sql.types import StringType
from pyspark.sql.functions import udf

def clean_text_logic(text: str) -> str:
    if not text:
        return ""
    
    # Remove HTML tags (basic regex approach, faster than parsing every row with BS4)
    text = re.sub('<[^<]+?>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove URL artifacts if any
    text = re.sub(r'http\S+', '', text)
    
    return text

# Register as UDF for use in Spark DataFrames
clean_text_udf = udf(clean_text_logic, StringType())
