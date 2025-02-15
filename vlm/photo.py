from pydantic import BaseModel
from openai import OpenAI
import base64
import numpy as np
from typing import List
from PIL import Image
import io
import requests
import pandas as pd
import json
# client = OpenAI()
import dotenv
import os

dotenv.load_dotenv()

class Weights(BaseModel):
    kind_of_food: List[str]
    weights_of_specific_kind_in_g: List[float]
    
def encode_image_from_np(image_array):
    if image_array.dtype != np.uint8:
        image_array = (255 * image_array).astype(np.uint8)
    image = Image.fromarray(image_array)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG") 
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return img_base64

    
def calculate_nutrition(image_array):
    # base64_image = encode_image_from_np(image_array)
    # completion = client.beta.chat.completions.parse(
    #     model="gpt-4o",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": [
    #                  {"type": "text", "text": "please identify the food in the image and estimate the weight of each kind of food (unit: g), return a table"},
    #                 {
    #                     "type": "image_url",
    #                     "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
    #                 },
    #             ],
    #         }
    #     ],
    #     response_format=Weights,
    # )
    # kind_and_weights=completion.choices[0].message.content
    # kind_and_weights=json.loads(kind_and_weights)
    # print(kind_and_weights)
    kind_and_weights={'kind_of_food': ['apple', 'banana', 'orange','chicken'], 'weights_of_specific_kind_in_g': [100, 100, 100,100]}
    API_KEY = os.getenv('USDA_API_KEY')      
    nutrient_mapping = {
        "Energy": "calories",
        "Potassium, K": "potassium",
        "Protein": "protein",
        "Carbohydrate, by difference": "carbs",
        "Total lipid (fat)": "fat"
    }
    
    nutrient_data = {nutrient: [] for nutrient in nutrient_mapping.values()}
    nutrient_data["food"] = [] 
    for i in range(len(kind_and_weights['kind_of_food'])):
        SEARCH_QUERY=kind_and_weights['kind_of_food'][i]
        URL = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={SEARCH_QUERY}&api_key={API_KEY}"
        response = requests.get(URL)
        data = response.json()
        if 'foods' not in data or len(data['foods']) == 0:
            print(f"Didn't fins {SEARCH_QUERY} in the database")
            continue
        food_nutrients = data['foods'][0]['foodNutrients']
    
        nutrient_values = {nutrient: None for nutrient in nutrient_mapping.values()}
        for nutrient in food_nutrients:
            name = nutrient.get("nutrientName", "")
            value = nutrient.get("value", None)
            if name in nutrient_mapping:
                nutrient_values[nutrient_mapping[name]] = value*kind_and_weights['weights_of_specific_kind_in_g'][i]/100
        
        nutrient_data["food"].append(SEARCH_QUERY)
        for key in nutrient_mapping.values():
            nutrient_data[key].append(nutrient_values[key])
    return nutrient_data
        

if __name__ == "__main__":
    image_path = "/Users/shuixianli/Desktop/1.jpg"
    image = Image.open(image_path)
    image_array = np.array(image)
    nutrient_data=calculate_nutrition(image_array)
    # show in table
    df = pd.DataFrame(nutrient_data)
    print(df)
    
        