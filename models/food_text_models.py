from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer_vi2en = AutoTokenizer.from_pretrained(
    "vinai/vinai-translate-vi2en-v2",
    use_fast=False,
    src_lang="vi_VN",
    tgt_lang="en_XX"
)
model_vi2en = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-vi2en-v2")

def translate_vi2en(vi_text: str) -> str:
    inputs = tokenizer_vi2en(vi_text, return_tensors="pt")
    decoder_start_token_id = tokenizer_vi2en.lang_code_to_id["en_XX"]
    outputs = model_vi2en.generate(
        **inputs,
        decoder_start_token_id=decoder_start_token_id,
        num_beams=5,
        early_stopping=True
    )
    return tokenizer_vi2en.decode(outputs[0], skip_special_tokens=True)

from models.Food_Extract.food_model import FoodModel
model = FoodModel()

def predict(text: str) -> dict:
    print(f"Input text: {text}")
    text_en = translate_vi2en(text)
    res = model.extract_foods(text_en)

    print(f"Extracted ingredients: {res}")
    unique_ingredients = [
        ing['text']
        for record in res
        for ing in record.get('Ingredient', [])
    ]

    print(f"Unique ingredients: {unique_ingredients}")
    return unique_ingredients
