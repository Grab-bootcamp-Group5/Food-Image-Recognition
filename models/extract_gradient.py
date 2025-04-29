import os
import time
import logging
from datetime import datetime
import json
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_FOLDER, 'extract_food_ingredients.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rate limiting: 25 requests/minute
def respect_rate_limit():
    interval = 60 / 25
    time.sleep(interval)


def analyze_food(dish_name: str, retries: int = 3) -> dict:
    """
    Calls the Gemini API to extract ingredients for the given dish name.
    """
    prompt = f"""
    List the most important ingredients to cook \"{dish_name}\".
    Return a JSON array named \"ingredients\", where each element has:
    - ingredient_name (string)
    - total unit (must include how much \"g\" for solids or \"ml\" for liquids and separateted by a white space):
    - category: classify the ingredients into these list of given categories:
    CATEGORIES = [
    "Prepared Vegetables", "Vegetables", "Fresh Fruits", "Fresh Meat",
    "Seafood & Fish Balls", "Instant Foods", "Ice Cream & Cheese", "Cakes",
    "Dried Fruits", "Candies", "Fruit Jam", "Snacks", "Milk", "Yogurt",
    "Alcoholic Beverages", "Beverages", "Seasonings", "Grains & Staples",
    "Cold Cuts: Sausages & Ham", "Cereals & Grains"]"""

    default = {"dish": dish_name, "ingredients": []}

    for attempt in range(1, retries + 1):
        try:
            respect_rate_limit()
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=[prompt]
            )
            text = response.text.strip()
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                payload = text[start:end]
                data = json.loads(payload)
                if isinstance(data, dict) and data.get('ingredients') is not None:
                    logger.info(f"Extracted ingredients for '{dish_name}'")
                    return data
            logger.warning(f"Unexpected response structure (attempt {attempt})")
        except Exception as e:
            logger.warning(f"Error on attempt {attempt} for '{dish_name}': {e}")
        time.sleep(2 ** attempt)

    logger.error(f"Failed to analyze '{dish_name}' after {retries} attempts")
    return default

def extract_food_ingredients(dish_name: str) -> dict:
    """
    Main function to extract food ingredients.
    """
    logger.info(f"Starting analysis for '{dish_name}'")
    result = analyze_food(dish_name)
    if result:
        logger.info(f"Analysis completed for '{dish_name}'")
        return result
    else:
        logger.error(f"Failed to extract ingredients for '{dish_name}'")
        return {"dish": dish_name, "ingredients": []}
