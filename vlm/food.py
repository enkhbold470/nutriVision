import requests
import pandas as pd

API_KEY = "LwoY2OBmIeqV69Faow5ZhH7HNKu2PuyyZgO7Oap3"
SEARCH_QUERY = "Garnish (Chili, Green Onion)"  # 你想要搜索的食物名称
URL = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={SEARCH_QUERY}&api_key={API_KEY}"

response = requests.get(URL)
data = response.json()

# 打印结果
print(type(data['foods'][0]))
print(data['foods'][0]['foodNutrients'][0]['value'])
df = pd.DataFrame(data['foods'][0]['foodNutrients'])
print(df)
if "foods" in data:
    for food in data["foods"][:3]:  # 仅显示前3个结果
        print(f"名称: {food['description']}")
        print(f"FDC ID: {food['fdcId']}")
        print(f"数据来源: {food['dataType']}\n")
else:
    print("未找到相关食物数据。")
