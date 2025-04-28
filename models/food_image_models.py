from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

model = load_model('best_model_101class.keras', compile=False)
with open('food_names.csv', 'r') as f:
    foods_sorted = sorted(f.read().splitlines())

def predict(img_path: str) -> str:
    img = image.load_img(img_path, target_size=(200, 200))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0) / 255.0
    pred = model.predict(img)
    return foods_sorted[np.argmax(pred)]
