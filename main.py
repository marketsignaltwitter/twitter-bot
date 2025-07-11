from keep_alive import keep_alive
keep_alive()

import tweepy
import schedule
import time
import random
from datetime import datetime
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

# ==== Load credentials from .env ====
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
CONSUMER_KEY = os.getenv("TWITTER_API_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

# ==== Tweepy Setup ====
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

# ==== Keywords ====
KEYWORDS = [
    "IPO", "funding", "merger", "SEBI", "RBI", "budget", "acquisition", "layoffs",
    "valuation", "stock crash", "earnings", "quarterly result", "investor",
    "SoftBank", "Tiger Global", "BlackRock", "TCS", "Infosys", "market rally",
    "record profit", "all-time high", "soars", "beats estimate", "strong earnings",
    "praised", "awarded", "recognized", "secured funding", "rising", "bullish",
    "expansion", "acquires", "backed by", "high demand", "investor interest"
]

# ==== Random Images ====
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
    except:
        return None
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
        print(f"Tweet error: {e}")
        return None

def contains_keyword(text):
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def is_new(title):
    try:
        with open("posted.txt", "r") as f:
            return title not in f.read().splitlines()
    except:
        return True

def save_title(title):
    with open("posted.txt", "a") as f:
        f.write(f"{title}\n")

def fetch_from_gnews():
    print("🔍 GNews check...")
    try:
        url = f"https://gnews.io/api/v4/search?q=stock%20market%20OR%20startup&lang=en&country=in&max=10&apikey={GNEWS_API_KEY}"
        articles = requests.get(url).json().get("articles", [])
        for article in articles:
            title = article.get("title", "")
            if contains_keyword(title) and is_new(title):
                link = article.get("url", "")
                save_title(title)
                return f"\U0001F4E2 {title}\n\n🔗 {link}\n\n#StockMarket #Finance #Startups #MarketSignalServices\n🕒 {datetime.utcnow().strftime('%H:%M UTC')}"
    except Exception as e:
        print(f"GNews error: {e}")
    return None

def fetch_from_newsdata():
    print("🔁 NewsData check...")
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q=stock%20market%20OR%20startup&language=en&country=in&category=business"
        articles = requests.get(url).json().get("results", [])
        for article in articles:
            title = article.get("title", "")
            if contains_keyword(title) and is_new(title):
                link = article.get("link", "")
                save_title(title)
                return f"\U0001F4E2 {title}\n\n🔗 {link}\n\n#StockMarket #Finance #Startups #MarketSignalServices\n🕒 {datetime.utcnow().strftime('%H:%M UTC')}"
    except Exception as e:
        print(f"NewsData error: {e}")
    return None

def fetch_market_news():
    return fetch_from_gnews() or fetch_from_newsdata()

def post_scheduled_tweet():
    tweet = fetch_market_news()
    if tweet:
        image_url = random.choice(IMAGES)
        print(f"\U0001F4DD Tweeting:\n{tweet[:100]}...")
        res = post_tweet_with_media(tweet, image_url)
        if res:
            print(f"✅ Tweet posted! ID: {res.data['id']}")
        else:
            print("❌ Tweet failed")
    else:
        print("⚠️ No news to tweet")

# Schedule every 30 minutes
schedule.every(30).minutes.do(post_scheduled_tweet)
print("🤖 Twitter bot started (every 30 min)")

while True:
    schedule.run_pending()
    time.sleep(1)

