import asyncio
import json
from app.kafka_client import producer
from app.config import settings
from app.logger import setup_logger

logger = setup_logger()

async def send_response(message: dict):
    try:
        await asyncio.to_thread(
            producer.send,
            settings.KAFKA_RESPONSE_TOPIC,
            value=json.dumps(message)
        )
        logger.info(f"Sent response: {message}")
    except Exception as e:
        logger.error(f"Failed to send response: {e}")
