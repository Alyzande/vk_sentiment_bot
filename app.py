from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import re

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
numeric_map = {"Negative": -1, "Neutral": 0, "Positive": 1}
reverse_numeric_map = {-1: "Negative", 0: "Neutral", 1: "Positive"}

# --- Home ---
@app.route('/')
def home():
    return render_template('index.html')

# --- Analyze posts from TASS, Kommersant, or RT ---
@app.route('/analyze', methods=['POST'])
def analyze_posts():
    data = request.get_json()
    news_service = data.get("news_service", "tass")
    count = data.get("count", 100)
    keywords = data.get("keywords", [])

    VK_TOKEN = os.getenv("VK_ACCESS_TOKEN")
    if not VK_TOKEN:
        return jsonify({"error": "VK access token not set"}), 500

    # Map frontend dropdown → VK group domains
    news_sources = {
        "tass": "tassagency",
        "kommersant": "kommersant",
        "rt": "rt_russian"
    }
    group_domain = news_sources.get(news_service, "tassagency")

    result = {"steps": {}}

    # Step 1: Get group info
    try:
        resp = requests.get(
            "https://api.vk.com/method/groups.getById",
            params={"group_id": group_domain, "access_token": VK_TOKEN, "v": "5.131"}
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

    # Step 2: Fetch posts
    try:
        resp = requests.get(
            "https://api.vk.com/method/wall.get",
            params={"owner_id": -group_id, "count": count, "access_token": VK_TOKEN, "v": "5.131"}
        ).json()

        posts = resp.get("response", {}).get("items", [])
        result["steps"]["posts_fetched"] = len(posts)
        # Debug preview of first 5 raw posts
        result["steps"]["posts_fetched_preview"] = [p.get("text", "")[:200] for p in posts[:5]]
        if not posts:
            return jsonify(result), 200

    except Exception as e:
        result["steps"]["posts_fetched"] = f"Exception: {str(e)}"
        return jsonify(result), 500

    # Step 3: Filter posts by keywords
    filtered_posts = []
    keyword_patterns = [re.compile(re.escape(kw.lower())) for kw in keywords]

    for post in posts:
        text = post.get("text", "")
        if not text:
            continue
        text_clean = re.sub(r"[^\w\s]", "", text.lower())
        if keywords:
            if any(p.search(text_clean) for p in keyword_patterns):
                filtered_posts.append(text)
        else:
            filtered_posts.append(text)

    result["steps"]["posts_matching_keywords"] = len(filtered_posts)
    if not filtered_posts:
        result["steps"]["raw_posts_preview"] = [p.get("text", "")[:200] for p in posts[:5]]
        return jsonify(result), 200

    # Step 4: Sentiment analysis per clause with fluff removal and mean aggregation
    analyzed_posts = []

    for text in filtered_posts[:20]:  # limit for speed
        clauses_raw = re.split(r'[.:]', text)
        clauses = []

        numeric_values = []

        for clause in clauses_raw:
            clause_clean = clause.strip()
            if not clause_clean:
                continue
            # Skip fluff
            if any(fluff in clause_clean.lower() for fluff in ["http", "https", "vk", "cc/", "max"]):
                continue

            analysis = classifier(clause_clean)[0]
            sentiment = label_map.get(analysis["label"], analysis["label"])
            numeric = numeric_map.get(sentiment, 0)
            numeric_values.append(numeric)
            clauses.append({"text": clause_clean, "sentiment": sentiment})

        # Aggregate via mean
        overall_numeric = 0
        if numeric_values:
            mean_value = sum(numeric_values) / len(numeric_values)
            overall_numeric = round(mean_value)
        overall_sentiment = reverse_numeric_map.get(overall_numeric, "Neutral")

        analyzed_posts.append({
            "text_full": text,
            "clauses": clauses,
            "sentiment": overall_sentiment
        })

    result["steps"]["analyzed_posts"] = analyzed_posts

    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
