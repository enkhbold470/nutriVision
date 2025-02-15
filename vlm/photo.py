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
    kind_and_weights={'kind_of_food': ['apple', 'banana', 'orange','chicken'], 'weights_of_specific_kind_in_g': [100, 200, 300,100]}



    API_KEY = "LwoY2OBmIeqV69Faow5ZhH7HNKu2PuyyZgO7Oap3"
    for i in range(len(kind_and_weights)):
        SEARCH_QUERY=kind_and_weights['kind_of_food'][i]
        URL = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={SEARCH_QUERY}&api_key={API_KEY}"
        response = requests.get(URL)
        data = response.json()
        data['foods'][0]['foodNutrients'][0]['value']
        df = pd.DataFrame(data['foods'][0]['foodNutrients'])
        

if __name__ == "__main__":
    image_path = "/Users/shuixianli/Desktop/1.jpg"
    image = Image.open(image_path)
    image_array = np.array(image)
    calculate_nutrition(image_array)
        