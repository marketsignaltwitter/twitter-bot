!pip install tweepy schedule requests python-dotenv

import tweepy
import schedule
import time
import random
from datetime import datetime
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

# ========================
# 🔒 Load from .env
# ========================
load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
CONSUMER_KEY = os.getenv("TWITTER_API_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

# ========================
# 🐦 Tweepy Setup
# ========================
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# ========================
# 🧠 Keywords
# ========================
KEYWORDS = [
    # Market Impact
    "IPO", "funding", "merger", "SEBI", "RBI", "budget", "acquisition", "layoffs",
    "valuation", "stock crash", "earnings", "quarterly result", "investor",
    "SoftBank", "Tiger Global", "BlackRock", "TCS", "Infosys", "market rally",
    
    # Tarif / Positive
    "record profit", "all-time high", "soars", "beats estimate", "strong earnings",
    "praised", "awarded", "recognized", "secured funding", "rising", "bullish",
    "expansion", "acquires", "backed by", "high demand", "investor interest"
]

# ========================
# 🖼️ Random Images
# ========================
IMAGES = [
    "https://images.unsplash.com/photo-1554224154-22dec7ec8818",
    "https://images.unsplash.com/photo-1612831190890-6f5cc84df012",
    "https://images.unsplash.com/photo-1605902711622-cfb43c4437d5"
]

def download_image(url):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return BytesIO(response.content)
        return None
    except Exception as e:
        print(f"Image download error: {e}")
        return None

def post_tweet_with_media(text, image_url=None):
    try:
        media_id = None
        if image_url:
            image_data = download_image(image_url)
            if image_data:
                media = api_v1.media_upload(filename="temp.jpg", file=image_data)
                media_id = media.media_id

        response = client.create_tweet(
            text=text,
            media_ids=[media_id] if media_id else None
        )
        return response
    except Exception as e:
        print(f"Tweet posting error: {e}")
        return None

def contains_keyword(text):
    lower_text = text.lower()
    return any(keyword.lower() in lower_text for keyword in KEYWORDS)

def fetch_from_gnews():
    try:
        print("🔍 Checking GNews...")
        url = f"https://gnews.io/api/v4/search?q=india%20stock%20market%20OR%20startup&lang=en&country=in&max=10&apikey={GNEWS_API_KEY}"
        response = requests.get(url)
        articles = response.json().get("articles", [])
        for article in articles:
            title = article.get("title", "")
            if contains_keyword(title):
                link = article.get("url", "")
                return f"📢 {title}\n\n🔗 {link}\n\n#StockMarket #Startups #MarketSignalServices\n🕒 {datetime.utcnow().strftime('%H:%M UTC')}"
        return None
    except Exception as e:
        print(f"GNews fetch error: {e}")
        return None

def fetch_from_newsdata():
    try:
        print("🔁 Checking NewsData.io...")
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q=india%20stock%20market%20OR%20startup&language=en&country=in&category=business"
        response = requests.get(url)
        articles = response.json().get("results", [])
        for article in articles:
            title = article.get("title", "")
            if contains_keyword(title):
                link = article.get("link", "")
                return f"📢 {title}\n\n🔗 {link}\n\n#StockMarket #Startups #MarketSignalServices\n🕒 {datetime.utcnow().strftime('%H:%M UTC')}"
        return None
    except Exception as e:
        print(f"NewsData fetch error: {e}")
        return None

def fetch_market_moving_news():
    news = fetch_from_gnews()
    if news:
        return news

    news = fetch_from_newsdata()
    if news:
        return news

    return None

def post_scheduled_tweet():
    try:
        tweet_text = fetch_market_moving_news()
        if not tweet_text:
            print("⚠️ No impactful news found.")
            return

        image_url = random.choice(IMAGES)
        print(f"📝 Tweet: {tweet_text[:100]}...")

        response = post_tweet_with_media(tweet_text, image_url)

        if response:
            print(f"✅ Tweet posted! ID: {response.data['id']}")
        else:
            print("❌ Tweet failed")
    except Exception as e:
        print(f"❌ Error: {e}")

# ========================
# ⏰ Schedule
# ========================
schedule.every(30).minutes.do(post_scheduled_tweet)

print("🤖 Smart Twitter Bot Started (Every 30 min)")
while True:
    schedule.run_pending()
    time.sleep(1)
