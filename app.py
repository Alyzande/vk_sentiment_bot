from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from collections import Counter

# Initialize app
app = Flask(__name__)
CORS(app)
load_dotenv()

# Load Russian sentiment model
print("Loading Russian sentiment model...")
model_name = "sismetanin/rubert-ru-sentiment-rusentiment"
classifier = pipeline("sentiment-analysis", model=model_name)
print("Model loaded successfully!")

label_map = {"LABEL_0": "Negative", "LABEL_1": "Neutral", "LABEL_2": "Positive"}

# --- Home ---
@app.route('/')
def home():
    return render_template('index.html')

# --- Analyze TASS posts ---
@app.route('/analyze_tass', methods=['POST'])
def analyze_tass_posts():
    """
    Expects JSON:
    {
        "count": 100,           # optional, default 100 posts
        "keywords": ["политика", "экономика"]
    }
    """
    data = request.get_json()
    count = data.get("count", 100)
    keywords = data.get("keywords", [])

    VK_TOKEN = os.getenv("VK_ACCESS_TOKEN")
    if not VK_TOKEN:
        return jsonify({"error": "VK access token not set"}), 500

    result = {"steps": {}}

    # Step 1: Get TASS group info
    tass_domain = "tassagency"
    try:
        resp = requests.get(
            "https://api.vk.com/method/groups.getById",
            params={"group_id": tass_domain, "access_token": VK_TOKEN, "v": "5.131"}
        ).json()

        if "error" in resp:
            result["steps"]["connect_to_group"] = f"Failed: {resp['error']}"
            return jsonify(result), 400
        else:
            group_id = resp["response"][0]["id"]
            result["steps"]["connect_to_group"] = f"Success, group_id={group_id}"

    except Exception as e:
        result["steps"]["connect_to_group"] = f"Exception: {str(e)}"
        return jsonify(result), 500

    # Step 2: Fetch posts from wall
    try:
        resp = requests.get(
            "https://api.vk.com/method/wall.get",
            params={"owner_id": -group_id, "count": count, "access_token": VK_TOKEN, "v": "5.131"}
        ).json()

        posts = resp.get("response", {}).get("items", [])
        result["steps"]["posts_fetched"] = len(posts)
        if not posts:
            return jsonify(result), 200

        # DEBUG: return first 10 raw posts so you can see what is actually posted
        result["steps"]["raw_posts_preview"] = [p.get("text", "") for p in posts[:10]]

    except Exception as e:
        result["steps"]["posts_fetched"] = f"Exception: {str(e)}"
        return jsonify(result), 500

    # Step 3: Filter posts by keywords (case-insensitive)
    filtered_posts = []
    for post in posts:
        text = post.get("text", "")
        if not text:
            continue
        text_lower = text.lower()
        if keywords:
            for kw in keywords:
                if kw.lower() in text_lower:
                    filtered_posts.append(text)
                    break
        else:
            filtered_posts.append(text)

    result["steps"]["posts_matching_keywords"] = len(filtered_posts)
    if not filtered_posts:
        return jsonify(result), 200

    # Step 4: Sentiment analysis
    sentiments = []
    for text in filtered_posts:
        analysis = classifier(text)[0]
        sentiment = label_map.get(analysis["label"], analysis["label"])
        sentiments.append(sentiment)

    # Step 5: Aggregate mode
    sentiment_mode = Counter(sentiments).most_common(1)[0][0]

    result["steps"]["sentiment_mode"] = sentiment_mode
    result["steps"]["all_filtered_posts_preview"] = filtered_posts[:5]  # first 5 posts for debug

    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
