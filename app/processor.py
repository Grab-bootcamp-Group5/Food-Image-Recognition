import asyncio
import json
from app.kafka_client import create_consumer
from app.minio_client import download_file
from models import food_image_models, food_text_models
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
        "requestMessage": {"type": "string"},
        "modelType": {"type": "string"},
    },
    "required": ["correlationId", "modelType"],
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
                correlationId = data.get('correlationId', None)
                logger.info(f"Correlation ID: {correlationId}")
                if data['modelType'] == 'image':
                    if 'fileName' not in data:
                        logger.warning("Missing fileName in message, skipping.")
                        continue
                    fileName = data['fileName']
                    tmp_path = f"/tmp/{fileName}"
                    download_file(fileName, tmp_path)
                    dish = food_image_models.predict(tmp_path)
                    logger.info(f"Predicted dish: {dish}")
                    ingredients = extract_food_ingredients(dish)
                    # logger.info(f"Extracted ingredients: {ingredients}")
                    payload = {
                        "dish": dish,
                        "correlationId": correlationId,
                        "ingredients": ingredients,
                        "modelType": data['modelType'],
                    }
                    await send_response(payload)
                elif data['modelType'] == 'text':
                    if 'requestMessage' not in data:
                        logger.warning("Missing requestMessage in message, skipping.")
                        continue
                    dish = data['requestMessage']
                    ingredients = food_text_models.predict(dish)
                    payload = {
                        "dish": dish,
                        "correlationId": correlationId,
                        "ingredients": ingredients,
                        "modelType": data['modelType'],
                    }
                    await send_response(payload)
                
            except Exception as e:
                logger.warning(f"Skip malformed message: {e}")
                continue
           