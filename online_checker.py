import sys
sys.stdout.reconfigure(line_buffering=True)  # THE ONLY ADDITION TO YOUR CODE

from googlesearch import search
from bs4 import BeautifulSoup
import requests
from difflib import SequenceMatcher

# 🔍 Get top result URLs
def get_top_results(query, num_results=3):
    urls = []
    try:
        print(f"\n🔍 Searching online for: \"{query}\"\n")
        for j in search(query, num_results=num_results, lang="en"):
            urls.append(j)
    except Exception as e:
        print(f"\n❌ Failed to fetch search results: {e}")
    return urls

# 🌐 Fetch page title for a given URL
def fetch_page_title(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.title.string if soup.title else "No Title"
        return title.strip()
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return "No Title"

# 🧠 Compare similarity between user input and fetched titles
def compare_similarity(news_input, titles):
    max_score = 0
    for title in titles:
        score = SequenceMatcher(None, news_input.lower(), title.lower()).ratio()
        if score > max_score:
            max_score = score
    return max_score

# 🔎 Main function: perform online search and check similarity
def check_news_online(news_input):
    urls = get_top_results(news_input)
    titles = [fetch_page_title(url) for url in urls]

    print("\n📰 Top Search Result Titles:")
    for idx, title in enumerate(titles):
        print(f"{idx + 1}. {title}")

    similarity = compare_similarity(news_input, titles)
    print(f"\n🧠 Similarity score: {similarity:.2f}")

    if similarity > 0.5:
        return "✅ Looks like REAL news"
    else:
        return "⚠️ Might be FAKE or not covered by major sources"