from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from collections import Counter
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
        # Add debug preview of first 5 raw posts
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

    # Step 4: Sentiment analysis per clause
    analyzed_posts = []
    sentiments = []

    for text in filtered_posts[:20]:  # limit for speed
        # Split text into clauses by punctuation
        clauses = re.split(r'[.,;:—]', text)
        clauses = [c.strip() for c in clauses if c.strip()]

        clause_sentiments = []
        for clause in clauses[:20]:  # limit to first 20 clauses
            analysis = classifier(clause)[0]
            clause_sentiments.append(label_map[analysis['label']])

        # Aggregate post sentiment (majority vote)
        if clause_sentiments:
            overall_sentiment = Counter(clause_sentiments).most_common(1)[0][0]
        else:
            overall_sentiment = "Neutral"

        sentiments.append(overall_sentiment)
        analyzed_posts.append({
            "text_full": text,
            "clauses": list(zip(clauses, clause_sentiments)),
            "sentiment": overall_sentiment
        })

    # Step 5: Aggregate overall sentiment
    sentiment_mode = Counter(sentiments).most_common(1)[0][0]

    result["steps"]["sentiment_mode"] = sentiment_mode
    result["steps"]["analyzed_posts"] = analyzed_posts

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
