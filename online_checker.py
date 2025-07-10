# Import required libraries
from googlesearch import search  # to perform Google searches
from bs4 import BeautifulSoup    # to parse HTML content
import requests                  # to make web requests
from difflib import SequenceMatcher  # to compare text similarity

# 🔍 Function to get top search results (URLs) from Google
def get_top_results(query, num_results=3):
    urls = []
    try:
        # Perform a Google search and collect the top result URLs
        for j in search(query, num_results=num_results, lang="en"):
            urls.append(j)
    except Exception as e:
        print("Search error:", e)
    return urls

# 🌐 Function to fetch the title of a webpage (used to compare with user's news)
def fetch_page_title(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}  # Prevent blocking by websites
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Extract the page's title tag
        title = soup.title.string if soup.title else "No Title"
        return title.strip()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

# 🔁 Function to compare the user-input news with fetched titles
def compare_similarity(news_input, titles):
    max_score = 0
    for title in titles:
        # Compare similarity between input and title
        score = SequenceMatcher(None, news_input.lower(), title.lower()).ratio()
        if score > max_score:
            max_score = score  # Save the highest similarity score
    return max_score

# 🧠 Main function that does the full online check
def check_news_online(news_input):
    print(f"🔍 Searching online for: \"{news_input}\"\n")
    
    # Step 1: Get top Google result URLs
    urls = get_top_results(news_input)

    # Step 2: Fetch their titles
    titles = [fetch_page_title(url) for url in urls]

    # Step 3: Display the titles to the user
    print("📰 Top Search Result Titles:")
    for i, title in enumerate(titles):
        print(f"{i+1}. {title}")

    # Step 4: Compare similarity between input news and fetched titles
    similarity = compare_similarity(news_input, titles)
    print(f"\n🧠 Similarity score: {similarity:.2f}")

    # Step 5: Decide if it's likely real or fake
    if similarity > 0.6:
        return "✅ Looks like REAL news"
    else:
        return "⚠️ Might be FAKE or not covered by major sources"

# 🧪 Test the module directly
if __name__ == "__main__":
    news = input("Enter the news headline or sentence:\n> ")
    result = check_news_online(news)
    print("\nResult:", result)
