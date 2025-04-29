import asyncio
import json
from app.kafka_client import create_consumer
from app.minio_client import download_file
from models.food_image_models import predict
from models.extract_gradient import extract_food_ingredients
from utils.async_helper import send_response
from app.logger import setup_logger

logger = setup_logger()

async def consume_messages():
    consumer = create_consumer()
    for message in consumer:
        if message and message.value:
            data = message.value
            logger.info(f"Received: {data}")
            if 'file_name' in data:
                file_name = data['file_name']
                tmp_path = f"/tmp/{file_name}"
                download_file(file_name, tmp_path)

                dish = predict(tmp_path)
                ingredients = extract_food_ingredients(dish)
                # logger.info(f"Extracted ingredients: {ingredients}")
                await send_response(ingredients)
            else:
                logger.warning("Missing 'file_name' in message")
