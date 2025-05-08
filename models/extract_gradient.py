import os
import time
import logging
from datetime import datetime
import json
from google import genai
import os
from dotenv import load_dotenv
from string import Template
import re

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


def analyze_food(dish_list: list, retries: int = 3) -> dict:
    """
    Calls the Gemini API to extract ingredients for the given dish name.
    """
    dish_list_str = json.dumps(dish_list, ensure_ascii=False, indent=2)
    logger.info(f"Analyzing dishes: {dish_list_str}")
    categories_mapping = {
        "Thịt heo": "Fresh Meat",
        "Thịt bò": "Fresh Meat",
        "Thịt gà, vịt, chim": "Fresh Meat",
        "Thịt sơ chế": "Fresh Meat",
        "Trứng gà, vịt, cút": "Fresh Meat",
        "Cá, hải sản, khô": "Seafood & Fish Balls",
        "Cá hộp": "Instant Foods",
        "Lạp xưởng": "Cold Cuts: Sausages & Ham",
        "Xúc xích": "Cold Cuts: Sausages & Ham",
        "Heo, bò, pate hộp": "Instant Foods",
        "Chả giò, chả ram": "Instant Foods",
        "Chả lụa, thịt nguội": "Cold Cuts: Sausages & Ham",
        "Xúc xích, lạp xưởng tươi": "Cold Cuts: Sausages & Ham",
        "Cá viên, bò viên": "Instant Foods",
        "Thịt, cá đông lạnh": "Instant Foods",

        "Trái cây": "Fresh Fruits",
        "Rau lá": "Vegetables",
        "Củ, quả": "Vegetables",
        "Nấm các loại": "Vegetables",
        "Rau, củ làm sẵn": "Vegetables",
        "Rau củ đông lạnh": "Vegetables",

        "Đồ chay ăn liền": "Instant Foods",
        "Đậu hũ, đồ chay khác": "Instant Foods",
        "Đậu hũ, tàu hũ": "Instant Foods",

        "Ngũ cốc": "Cereals & Grains",
        "Ngũ cốc, yến mạch": "Cereals & Grains",
        "Gạo các loại": "Grains & Staples",
        "Bột các loại": "Grains & Staples",
        "Đậu, nấm, đồ khô": "Grains & Staples",

        "Mì ăn liền": "Instant Foods",
        "Phở, bún ăn liền": "Instant Foods",
        "Hủ tiếu, miến": "Instant Foods",
        "Miến, hủ tiếu, phở khô": "Instant Foods",
        "Mì Ý, mì trứng": "Instant Foods",
        "Cháo gói, cháo tươi": "Instant Foods",
        "Bún các loại": "Instant Foods",
        "Nui các loại": "Instant Foods",
        "Bánh tráng các loại": "Instant Foods",
        "Bánh phồng, bánh đa": "Instant Foods",
        "Bánh gạo Hàn Quốc": "Cakes",

        "Nước mắm": "Seasonings",
        "Nước tương": "Seasonings",
        "Tương, chao các loại": "Seasonings",
        "Tương ớt - đen, mayonnaise": "Seasonings",
        "Dầu ăn": "Seasonings",
        "Dầu hào, giấm, bơ": "Seasonings",
        "Gia vị nêm sẵn": "Seasonings",
        "Muối": "Seasonings",
        "Hạt nêm, bột ngọt, bột canh": "Seasonings",
        "Tiêu, sa tế, ớt bột": "Seasonings",
        "Bột nghệ, tỏi, hồi, quế,...": "Seasonings",
        "Nước chấm, mắm": "Seasonings",
        "Mật ong, bột nghệ": "Seasonings",

        "Sữa tươi": "Milk",
        "Sữa đặc": "Milk",
        "Sữa pha sẵn": "Milk",
        "Sữa hạt, sữa đậu": "Milk",
        "Sữa ca cao, lúa mạch": "Milk",
        "Sữa trái cây, trà sữa": "Milk",
        "Sữa chua ăn": "Yogurt",
        "Sữa chua uống liền": "Yogurt",
        "Bơ sữa, phô mai": "Milk",

        "Bia, nước có cồn": "Alcoholic Beverages",
        "Rượu": "Alcoholic Beverages",
        "Nước trà": "Beverages",
        "Nước ngọt": "Beverages",
        "Nước ép trái cây": "Beverages",
        "Nước yến": "Beverages",
        "Nước tăng lực, bù khoáng": "Beverages",
        "Nước suối": "Beverages",
        "Cà phê hoà tan": "Beverages",
        "Cà phê pha phin": "Beverages",
        "Cà phê lon": "Beverages",
        "Trà khô, túi lọc": "Beverages",

        "Bánh tươi, Sandwich": "Cakes",
        "Bánh bông lan": "Cakes",
        "Bánh quy": "Cakes",
        "Bánh snack, rong biển": "Snacks",
        "Bánh Chocopie": "Cakes",
        "Bánh gạo": "Cakes",
        "Bánh quế": "Cakes",
        "Bánh que": "Cakes",
        "Bánh xốp": "Cakes",
        "Kẹo cứng": "Candies",
        "Kẹo dẻo, kẹo marshmallow": "Candies",
        "Kẹo singum": "Candies",
        "Socola": "Candies",
        "Trái cây sấy": "Dried Fruits",
        "Hạt khô": "Dried Fruits",
        "Rong biển các loại": "Snacks",
        "Rau câu, thạch dừa": "Fruit Jam",
        "Mứt trái cây": "Fruit Jam",
        "Cơm cháy, bánh tráng": "Snacks",

        "Làm sẵn, ăn liền": "Instant Foods",
        "Sơ chế, tẩm ướp": "Instant Foods",
        "Nước lẩu, viên thả lẩu": "Instant Foods",
        "Kim chi, đồ chua": "Instant Foods",
        "Mandu, há cảo, sủi cảo": "Instant Foods",
        "Bánh bao, bánh mì, pizza": "Instant Foods",
        "Kem cây, kem hộp": "Ice Cream & Cheese",
        "Bánh flan, thạch, chè": "Cakes",
        "Trái cây hộp, siro": "Fruit Jam",

        "Cá mắm, dưa mắm": "Seasonings",
        "Đường": "Seasonings",
        "Nước cốt dừa lon": "Seasonings",
        "Sữa chua uống": "Yogurt",
        "Khô chế biến sẵn": "Instant Foods"
    }
    category_set = sorted(set(categories_mapping.values()))
    category_list_str = '\n- ' + '\n- '.join(category_set)

    prompt_template = Template("""
        You are a food ingredient extraction assistant.

        Your job is to extract ingredients **only for the exact dish(es)** provided in the input list. Do NOT guess, infer, or add other dishes. The number of output dishes MUST match exactly the number of dishes in the input.

        ---

        ### Input format:
        A JSON array of informal user-described dishes in Vietnamese:

        $dish_list

        You must return a JSON object with the following format:

        {
        "dishes": [
            {
                "dish_name": "Beef Cheese Mushroom Pizza",
                "dish_vn_name": "Bánh pizza thịt bò phô mai nấm",
                "ingredients_must_have": [
                    {"ingredient_name": "Pizza dough", "ingredient_vn_name": "Bột bánh pizza", "total_unit": "250 g", "category": "Grains & Staples"},
                    {"ingredient_name": "Tomato sauce", "ingredient_vn_name": "Sốt cà chua", "total_unit": "100 ml", "category": "Seasonings"},
                    {"ingredient_name": "Mozzarella cheese", "ingredient_vn_name": "Phô mai Mozzarella", "total_unit": "100 g", "category": "Milk"},
                    {"ingredient_name": "Ground beef", "ingredient_vn_name": "Thịt bò xay", "total_unit": "100 g", "category": "Fresh Meat"},
                    {"ingredient_name": "Mushrooms", "ingredient_vn_name": "Nấm", "total_unit": "75 g", "category": "Vegetables"},
                    {"ingredient_name": "Olive oil", "ingredient_vn_name": "Dầu ô liu", "total_unit": "10 ml", "category": "Seasonings"},
                    {"ingredient_name": "Garlic", "ingredient_vn_name": "Tỏi", "total_unit": "5 g", "category": "Seasonings"},
                    {"ingredient_name": "Salt", "ingredient_vn_name": "Muối", "total_unit": "3 g", "category": "Seasonings"},
                    {"ingredient_name": "Sugar", "ingredient_vn_name": "Đường", "total_unit": "3 g", "category": "Seasonings"},
                    {"ingredient_name": "Yeast", "ingredient_vn_name": "Men nở", "total_unit": "3 g", "category": "Seasonings"},
                    {"ingredient_name": "Water", "ingredient_vn_name": "Nước", "total_unit": "100 ml", "category": "Seasonings"}
                ],
                "ingredients_optional": [
                    {"ingredient_name": "Oregano", "ingredient_vn_name": "Kinh giới cay", "total_unit": "2 g", "category": "Seasonings"},
                    {"ingredient_name": "Black pepper", "ingredient_vn_name": "Tiêu đen", "total_unit": "1 g", "category": "Seasonings"},
                    {"ingredient_name": "Parsley", "ingredient_vn_name": "Ngò tây", "total_unit": "1 g", "category": "Vegetables"}
                ]
                }

        ]
        }

        ---

        ### Ingredient rules:
        - `ingredient_name`: English name
        - `ingredient_vn_name`: Vietnamese name
        - `total_unit`: Required. Must be in the format `<amount> <unit>`, using only "g" or "ml"
        - `category`: Must match exactly one of these values: $mapping_str

        ---

        ### Strict constraints:
        - Do NOT add extra dishes not in the input
        - The output must contain exactly {$N} dish objects (equal to the input size)
        - Each `dish_name` must correspond only to the user-provided dish
        - Do NOT hallucinate other meals like “Pho” or “Bun Cha” if not in the input
        - Each `ingredients_must_have` list must be **complete enough to actually cook the dish from scratch**, assuming the user has no ingredients at home. This includes all base ingredients, seasonings, and cooking oils.

        If any essential item is missing (such as oil, garlic, salt, flour, water, etc.), your response is invalid.


        Only return the JSON object — do not explain, do not preface with text."""
    )
    prompt = prompt_template.substitute(
        dish_list=dish_list_str,
        mapping_str=category_list_str,
        N=len(dish_list)
    )
    default = {
        "dishes": [
            {
                "dish_name": d["dish_name"],
                "ingredients_must_have": [],
                "ingredients_optional": []
            } for d in dish_list
        ]
    }

    dish_names = [d["dish_name"] for d in dish_list]

    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=[prompt]
            )
            text = response.text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            logger.info(f"Response text: {text}")
            start = text.find('{')
            end = text.rfind('}') + 1

            if start >= 0 and end > start:

                payload = text[start:end]
                try:
                    data = json.loads(payload)
                    if isinstance(data, dict) and "dishes" in data:
                        logger.info(f"Extracted ingredients for dishes: {dish_names}")
                        return data
                except json.JSONDecodeError as je:
                    logger.warning(f"JSON decode error: {je}. Raw payload: {payload}")
            else:
                logger.warning(f"Cannot locate valid JSON structure in response.")

        except Exception as e:
            logger.warning(f"Error on attempt {attempt} for dishes {dish_names}: {e}")

        time.sleep(2 ** attempt)

    logger.error(f"Failed to analyze dishes {dish_names} after {retries} attempts. Last response: {text}")
    return default


def extract_food_ingredients(dish_list: list) -> dict:
    """
    Main function to extract food ingredients.
    """
    logger.info(f"Analyzing dishes: {[d['dish_name'] for d in dish_list]}")
    result = analyze_food(dish_list)
    print("2")
    if result:
        logger.info(f"Analysis completed for '{dish_list}'")
        return result
    else:
        logger.error(f"Failed to extract ingredients for '{dish_list}'")
        return {"dish": dish_list, "ingredients": []}
