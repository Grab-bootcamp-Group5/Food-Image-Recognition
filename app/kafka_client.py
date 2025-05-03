from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from app.config import settings
from app.logger import setup_logger
import json

logger = setup_logger()

def safe_json_deserializer(x):
    try:
        return json.loads(x.decode('utf-8'))
    except json.JSONDecodeError as e:
        logger.error(f"[Kafka] JSON decode failed: {e}")
        logger.error(f"[Kafka] Raw: {x}")
        return {}  # hoặc None nếu muốn skip hẳn


def create_consumer():
    try:
        return KafkaConsumer(
            settings.KAFKA_TOPIC,
            bootstrap_servers=[settings.KAFKA_BROKER],
            group_id=settings.KAFKA_GROUP,
            value_deserializer=safe_json_deserializer,
            enable_auto_commit=True
        )
    except KafkaError as e:
        logger.error(f"Kafka Consumer Connection Failed: {e}")
        raise

producer = KafkaProducer(
    bootstrap_servers=[settings.KAFKA_BROKER],
    value_serializer=lambda v: v.encode('utf-8')
)
