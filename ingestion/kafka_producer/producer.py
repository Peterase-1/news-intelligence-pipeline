
import json
import logging
from confluent_kafka import Producer
import socket
import yaml
import os

# Load Config
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../../config/kafka.yml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

logger = logging.getLogger(__name__)

class NewsProducer:
    def __init__(self):
        self.config = load_config()
        self.bootstrap_servers = self.config['kafka']['bootstrap_servers']
        self.topic = self.config['topics']['raw_news']
        
        conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': socket.gethostname(),
            'acks': 'all'   # Ensure data durability
        }
        
        self.producer = Producer(conf)
        logger.info(f"Kafka Producer initialized for topic: {self.topic}")

    def delivery_report(self, err, msg):
        """ Called once for each message produced to indicate delivery result. """
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def produce_news(self, article: dict):
        """
        Sends a single news article dictionary to Kafka.
        """
        try:
            # Serialize to JSON (assuming schema validation happens upstream or we trust the scraper)
            # In a stricter setup, we would validate against schema.py here
            value = json.dumps(article).encode('utf-8')
            key = article.get('url', '').encode('utf-8')

            self.producer.produce(
                self.topic,
                key=key,
                value=value,
                callback=self.delivery_report
            )
            
            # Trigger any available delivery report callbacks from previous produce() calls
            self.producer.poll(0)
            
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")

    def flush(self):
        """ Ensure all messages are sent before stopping """
        self.producer.flush()
        logger.info("Producer flushed.")
