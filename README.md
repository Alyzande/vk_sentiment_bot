# 📰 Russian News Sentiment Analyzer

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)  
[![Flask](https://img.shields.io/badge/flask-2.3-blue)](https://flask.palletsprojects.com/)  

A web app that analyzes sentiment in Russian news posts on VK, focusing on the Ukraine conflict.

---

## Overview

This application connects to VK using the VK API and fetches the latest posts from major Russian news agencies. It identifies posts related to specific keywords about the Ukrainian war, analyzes their sentiment using a Russian language sentiment model from Hugging Face, and presents an aggregated, easy-to-read summary.

**Key features:**

- Fetches the latest posts from VK public pages of news agencies such as **TASS**, **Kommersant**, and **RT**.  
- Filters posts for user-specified keywords related to the Ukrainian war.  
- Splits posts into fragments/clauses and analyzes each fragment individually for sentiment.  
- Aggregates fragment-level sentiment into an overall sentiment for the post.  
- Displays posts in a user-friendly interface with clear color-coded sentiment:  
  - **Positive** (blue)  
  - **Neutral** (gray)  
  - **Negative** (red)  
- Users can click **"Why [Positive/Neutral/Negative]?"** to view fragment-level sentiment reasoning.  

---

## How it Works

1. **Connect to VK API**  
   The app uses a VK API access token to access public news posts from selected news agency pages.  

2. **Fetch Posts**  
   For each selected news agency and keyword, the app fetches the top 100 recent posts.  

3. **Filter by Keywords**  
   Posts are filtered to include only those containing the specified keywords.  

4. **Sentiment Analysis**  
   - Posts are split into clauses/fragments using punctuation (`.` or `:`).  
   - Each fragment is analyzed with the Hugging Face [`sismetanin/rubert-ru-sentiment-rusentiment`](https://huggingface.co/sismetanin/rubert-ru-sentiment-rusentiment) model.  
   - Fluff such as URLs or promotional text is ignored.  

5. **Aggregate Sentiment**  
   - Fragment sentiment values are converted to numeric scores (`Positive = 1`, `Neutral = 0`, `Negative = -1`).  
   - Overall post sentiment is calculated as the **mean** of fragment scores.  

6. **Display Results**  
   - Posts are displayed with their overall sentiment.  
   - Users can optionally expand to see fragment-level analysis.  

---

## Requirements

- Python 3.10+  
- Flask  
- Flask-CORS  
- Transformers (Hugging Face)  
- Requests  
- python-dotenv  

---

## Setup

1. Clone the repository:

```bash
git clone <repo_url>
cd <repo_folder>
````

2. Create and activate a virtual environment:

```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your VK access token:

```env
VK_ACCESS_TOKEN=your_vk_access_token_here
```

5. Run the app:

```bash
python app.py
```

6. Open your browser at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## Usage

1. Select a **news service** (TASS, Kommersant, RT).
2. Choose a **keyword** related to the Ukrainian conflict.
3. Select the number of posts to fetch (default 100).
4. Click **Analyze** to view sentiment results.

---

## Notes

* Sentiment is calculated per clause to capture nuanced expressions.
* Clauses containing URLs, promotional text, or the word "Max" are ignored.
* The app does **not** access user data; it only reads public posts from VK.

