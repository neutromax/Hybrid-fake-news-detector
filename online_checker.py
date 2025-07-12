# online_checker.py

from googlesearch import search
from bs4 import BeautifulSoup
import requests
from difflib import SequenceMatcher

# 🔍 Function to get top search result URLs from Google
def get_top_results(query, num_results=3):
    urls = []
    try:
        print(f"🔍 Searching Google for: \"{query}\"\n")
        for j in search(query, num_results=num_results, lang="en"):
            urls.append(j)
    except Exception as e:
        print("❌ Search error:", e)
    return urls

# 🌐 Fetch page title from URL
def fetch_page_title(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No Title"
        print(f"📄 [DEBUG] Title fetched from {url}: {title}")
        return title
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return "No Title"

# 🧠 Compare similarity between input and page titles
def compare_similarity(news_input, titles):
    max_score = 0
    for title in titles:
        score = SequenceMatcher(None, news_input.lower(), title.lower()).ratio()
        if score > max_score:
            max_score = score
    return max_score

# 🔍 Main function: check news online
def check_news_online(news_input):
    print("\n🛠️ [DEBUG] Entered check_news_online()")
    print(f"📰 [DEBUG] Input headline: {news_input}")

    urls = get_top_results(news_input)
    if not urls:
        return "No internet or error checking online."

    titles = [fetch_page_title(url) for url in urls]

    print("\n📰 Top Search Result Titles:")
    for i, title in enumerate(titles):
        print(f"{i+1}. {title}")

    similarity = compare_similarity(news_input, titles)
    print(f"\n🧠 [DEBUG] Similarity Score: {similarity:.2f}")

    if similarity > 0.5:
        return "✅ Looks like REAL news"
    else:
        return "⚠️ Might be FAKE or not covered by major sources"
