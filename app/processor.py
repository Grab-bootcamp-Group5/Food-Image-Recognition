import asyncio
import json
from app.kafka_client import create_consumer
from app.minio_client import download_file
from models.food_image_models import predict
from models.extract_gradient import extract_food_ingredients
from utils.async_helper import send_response
from app.logger import setup_logger
from jsonschema import validate, ValidationError


logger = setup_logger()

schema = {
    "type": "object",
    "properties": {
        "correlationId": {"type": "string"},
        "fileName": {"type": "string"},
        "modelType": {"type": "string"},
    },
    "required": ["fileName", "correlationId", "modelType"],
}

async def consume_messages():
    consumer = create_consumer()
    for message in consumer:
        if message and message.value:
            try:
                data = message.value
                print(f"Received message: {data}")
                if not data:
                    logger.warning("Empty or invalid message received, skipping.")
                    continue

                try:
                    validate(instance=data, schema=schema)
                except ValidationError as e:
                    logger.warning(f"Message failed schema validation: {e}")
                    continue
                logger.info(f"Received: {data}")
                if 'fileName' in data:
                    fileName = data['fileName']
                    correlationId = data.get('correlationId', None)
                    logger.info(f"Correlation ID: {correlationId}")
                    tmp_path = f"/tmp/{fileName}"
                    download_file(fileName, tmp_path)

                    dish = predict(tmp_path)
                    ingredients = extract_food_ingredients(dish)
                    # logger.info(f"Extracted ingredients: {ingredients}")
                    payload = {
                        "dish": dish,
                        "correlationId": correlationId,
                        "ingredients": ingredients
                    }
                    await send_response(payload)
                else:
                    logger.warning("Missing 'fileName' in message")

            except Exception as e:
                logger.warning(f"Skip malformed message: {e}")
                continue
           