from google import genai
import os

client = genai.Client(api_key=os.getenv("AIzaSyDQTQD4EYzTVEkqyovwIcHoOipguS5bcjo"))

models = client.models.list()

for m in models:
    print(m.name)
