import asyncio
from app.processor import consume_messages

if __name__ == "__main__":
    asyncio.run(consume_messages())
