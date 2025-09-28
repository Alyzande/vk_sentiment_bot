import os
import requests
from dotenv import load_dotenv

load_dotenv()  # load VK_ACCESS_TOKEN from .env

TOKEN = os.getenv("VK_ACCESS_TOKEN")
if not TOKEN:
    print("VK_ACCESS_TOKEN not found in .env")
    exit()

# Try fetching 3 posts for a test hashtag
url = "https://api.vk.com/method/wall.search"
params = {
    "q": "#музыка",     # change this to any hashtag
    "count": 3,        # number of posts to fetch
    "access_token": TOKEN,
    "v": "5.199"
}

response = requests.get(url, params=params).json()
print(response)
