
import yaml
import os
from pyspark.sql import SparkSession

def load_spark_config():
    config_path = os.path.join(os.path.dirname(__file__), '../../../config/spark.yml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_spark_session(app_name: str = None):
    """
    Builds and returns a SparkSession with configuration from spark.yml.
    """
    config = load_spark_config()
    spark_conf = config['spark']
    
    name = app_name or spark_conf['app_name']
    master = spark_conf['master']
    packages = ",".join(spark_conf['packages'])
    
    builder = SparkSession.builder \
        .appName(name) \
        .master(master) \
        .config("spark.jars.packages", packages) \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint")
        
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel(spark_conf['log_level'])
    
    return spark
