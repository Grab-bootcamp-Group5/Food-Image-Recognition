from kafka import KafkaProducer
import json
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

kafka_broker_host = os.environ.get('KAFKA_BROKER_HOST')
kafka_broker_port = os.environ.get('KAFKA_BROKER_PORT')

if not kafka_broker_host or not kafka_broker_port:
    raise ValueError("Environment variables KAFKA_BROKER_HOST and KAFKA_BROKER_PORT must be set")

producer = KafkaProducer(
    bootstrap_servers=[f"{kafka_broker_host}:{kafka_broker_port}"],
    value_serializer=lambda v: v.encode('utf-8')
)

async def on_message(_, __, msg):

    try:
        message = {
        
            'file_name': "OIP.jpg",
            'bucket_name': "dish-meal"
        }
        print(f"Received message: {message}")
        # print("Sendingg.......")
        await asyncio.wait_for(
            asyncio.to_thread(
                producer.send,
                os.environ.get('KAFKA_FOOD_INGREDIENT_EXTRACT_TOPIC'),
                value=json.dumps(message)
            ),
            timeout=10  # Set timeout to 10 seconds
        )
    except Exception as e:
        print(f"Error while processing message: {e}")

async def main():
    try:
        # Simulate receiving a message
        await on_message(None, None, None)
    except Exception as e:
        print(f"Error in main: {e}")
if __name__ == '__main__':
    asyncio.run(main())
    producer.close()