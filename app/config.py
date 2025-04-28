import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    KAFKA_BROKER = f"{os.environ.get('KAFKA_BROKER_HOST')}:{os.environ.get('KAFKA_BROKER_PORT')}"
    KAFKA_TOPIC = os.environ.get('KAFKA_FOOD_INGREDIENT_EXTRACT_TOPIC')
    KAFKA_RESPONSE_TOPIC = os.environ.get('KAFKA_INGREDIENT_RESPONSE_TOPIC')
    KAFKA_GROUP = os.environ.get('KAFKA_CONSUMER_GROUP')

    MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT') + ':' + os.environ.get('MINIO_PORT')
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
    MINIO_BUCKET = os.environ.get('MINIO_BUCKET_NAME')

settings = Settings()
