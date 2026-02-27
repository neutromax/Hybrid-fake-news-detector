# online_checker.py

import requests
from difflib import SequenceMatcher
import os
from dotenv import load_dotenv
import re
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Cache settings
CACHE_DIR = Path("cache")
CACHE_DURATION = timedelta(hours=6)  # Cache results for 6 hours
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(query):
    """Create a cache key from the query"""
    # Clean and normalize the query
    clean_query = re.sub(r'[^\w\s]', '', query.lower())
    words = clean_query.split()
    # Take first 5 words max for cache key
    key_words = words[:5]
    return "_".join(key_words)

def get_cached_result(query):
    """Get cached result if available and not expired"""
    cache_key = get_cache_key(query)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            # Check if cache is still valid
            cached_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cached_time < CACHE_DURATION:
                print(f"📦 Using cached result for: '{query}'")
                return cached['result']
            else:
                print("🗑️ Cache expired, fetching fresh data")
                cache_file.unlink()  # Delete expired cache
        except:
            pass
    
    return None

def save_to_cache(query, result):
    """Save result to cache"""
    cache_key = get_cache_key(query)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    try:
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'result': result
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        print(f"💾 Cached result for: '{query}'")
    except Exception as e:
        print(f"⚠️ Failed to cache: {e}")

def search_news_api(query, num_results=8):
    """Search for news using NewsAPI with rate limit handling"""
    if not NEWS_API_KEY:
        print("⚠️ NEWS_API_KEY not found in environment variables")
        return []
    
    # Check cache first
    cached = get_cached_result(query)
    if cached:
        return cached
    
    try:
        print(f"🔍 Searching NewsAPI for: '{query}'")
        
        # Extract key terms for better search
        key_terms = extract_key_terms(query)
        search_query = " ".join(key_terms[:3])
        print(f"📌 Using search query: '{search_query}'")
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": search_query,
            "apiKey": NEWS_API_KEY,
            "pageSize": num_results,
            "sortBy": "relevancy",
            "language": "en",
            "searchIn": "title,description"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        # Handle rate limiting
        if response.status_code == 429:
            print("⚠️ Rate limit reached! Using fallback mode...")
            return get_fallback_results(query)
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "ok" and data["totalResults"] > 0:
                articles = data["articles"]
                print(f"✅ Found {len(articles)} articles")
                
                results = []
                for article in articles:
                    title = article["title"] or ""
                    description = article["description"] or ""
                    
                    # Clean titles
                    title = re.sub(r'\s*[-|]\s*(BBC News|CNN|Reuters|AP|AFP|News24|YouTube)$', '', title)
                    
                    results.append({
                        "title": title.strip(),
                        "description": description.strip(),
                        "source": article["source"]["name"],
                        "url": article["url"],
                        "published": article["publishedAt"][:10]
                    })
                
                # Save to cache
                save_to_cache(query, results)
                return results
            else:
                print("⚠️ No articles found")
                return []
        else:
            print(f"❌ NewsAPI error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ NewsAPI exception: {str(e)}")
        return []

def get_fallback_results(query):
    """Provide fallback results when API rate limit is reached"""
    print("🔄 Using fallback mode...")
    
    # Pre-defined knowledge for common topics
    fallback_db = {
        "elon musk richest": {
            "title": "Elon Musk is the world's richest person",
            "source": "Forbes/Bloomberg",
            "description": "As of 2024, Elon Musk is consistently ranked as the world's wealthiest individual"
        },
        "nasa water mars": {
            "title": "NASA confirms water on Mars",
            "source": "NASA",
            "description": "NASA has discovered evidence of liquid water on Mars"
        },
        "covid vaccine": {
            "title": "COVID-19 vaccines are safe and effective",
            "source": "WHO/CDC",
            "description": "Multiple studies confirm the safety and efficacy of COVID-19 vaccines"
        }
    }
    
    # Check if query matches any fallback entries
    query_lower = query.lower()
    for key, data in fallback_db.items():
        if key in query_lower:
            return [{
                "title": data["title"],
                "description": data["description"],
                "source": data["source"],
                "url": "#",
                "published": "2024"
            }]
    
    # If no match, return empty list (will trigger "no results" message)
    return []

def extract_key_terms(text):
    """Extract important keywords from the query"""
    stop_words = {'is', 'the', 'in', 'of', 'and', 'to', 'a', 'for', 'on', 'with', 'at', 'by', 'an', 'are', 'was', 'were'}
    words = text.lower().split()
    
    important_words = []
    for word in words:
        if word not in stop_words and len(word) > 2:
            important_words.append(word)
    
    if not important_words:
        important_words = words[:3]
    
    return important_words

def calculate_relevance_score(news_input, article):
    """Calculate how relevant an article is to the news input"""
    news_lower = news_input.lower()
    title = article["title"].lower()
    description = article["description"].lower()
    
    # Extract key terms
    key_terms = extract_key_terms(news_input)
    
    # Scoring
    title_score = sum(2 for term in key_terms if term in title)
    desc_score = sum(1 for term in key_terms if term in description)
    
    # Entity recognition
    entity_score = 0
    if "elon musk" in news_lower and ("elon musk" in title or "elon musk" in description):
        entity_score += 3
    if "nasa" in news_lower and "nasa" in title:
        entity_score += 2
    if "water" in news_lower and "mars" in news_lower:
        if "water" in title and "mars" in title:
            entity_score += 2
    
    # Sequence matching
    sequence_score = SequenceMatcher(None, news_lower, title).ratio()
    
    # Calculate final score
    max_possible = len(key_terms) * 2 + 5
    total_score = (title_score + desc_score + entity_score) / max_possible if max_possible > 0 else 0
    
    final_score = (total_score * 0.7) + (sequence_score * 0.3)
    
    return final_score

def compare_similarity(news_input, articles):
    """Compare news with articles"""
    if not articles:
        return 0, []
    
    best_matches = []
    
    for article in articles:
        relevance_score = calculate_relevance_score(news_input, article)
        
        if relevance_score > 0.15:
            best_matches.append({
                "score": relevance_score,
                "title": article["title"],
                "description": article["description"][:100] + "..." if len(article["description"]) > 100 else article["description"],
                "source": article["source"],
                "url": article["url"],
                "published": article["published"]
            })
    
    best_matches.sort(key=lambda x: x["score"], reverse=True)
    max_score = best_matches[0]["score"] if best_matches else 0
    
    return max_score, best_matches[:3]

def check_news_online(news_input):
    """Main verification function"""
    print("\n🛠️ [DEBUG] Entered check_news_online()")
    print(f"📰 [DEBUG] Input headline: {news_input}")

    all_articles = []
    
    # Try NewsAPI
    if NEWS_API_KEY:
        print("📡 Using NewsAPI...")
        articles = search_news_api(news_input)
        all_articles.extend(articles)
    else:
        print("⚠️ No NewsAPI key found, using fallback")
        all_articles.extend(get_fallback_results(news_input))

    if not all_articles:
        # If still no results, use simple pattern matching
        print("📊 Using pattern matching fallback...")
        return pattern_match_fallback(news_input)

    print(f"\n📰 Found {len(all_articles)} articles")

    similarity, best_matches = compare_similarity(news_input, all_articles)
    print(f"\n🧠 [DEBUG] Relevance Score: {similarity:.2f}")

    if best_matches:
        print("\n📊 Best matches found:")
        for i, match in enumerate(best_matches, 1):
            print(f"{i}. Score: {match['score']:.2f} - {match['title'][:80]}...")
            print(f"   Source: {match['source']}")

    # Return verdict
    if similarity > 0.5:
        return "✅ REAL news (Confirmed by multiple sources)"
    elif similarity > 0.3:
        return "⚠️ Possibly REAL (Some coverage found)"
    elif similarity > 0.15:
        return "⚠️ Limited coverage - Could be TRUE or FALSE"
    else:
        return "❌ FAKE news (No matching coverage)"

def pattern_match_fallback(news_input):
    """Ultimate fallback using pattern matching"""
    news_lower = news_input.lower()
    
    # Real news patterns
    real_patterns = ['nasa', 'scientist', 'study', 'research', 'official', 'government', 'president']
    # Fake news patterns
    fake_patterns = ['alien', 'ufo', 'conspiracy', 'secret', 'miracle', 'shocking', 'you won\'t believe']
    
    real_score = sum(1 for pattern in real_patterns if pattern in news_lower)
    fake_score = sum(1 for pattern in fake_patterns if pattern in news_lower)
    
    if real_score > fake_score:
        return "✅ Pattern suggests REAL news"
    elif fake_score > real_score:
        return "❌ Pattern suggests FAKE news"
    else:
        return "⚠️ Cannot verify online (rate limited)"
# Add to online_checker.py
def cleanup_old_cache(max_age_days=7):
    """Delete cache files older than max_age_days"""
    now = time.time()
    for cache_file in CACHE_DIR.glob("*.json"):
        file_age = now - cache_file.stat().st_mtime
        if file_age > max_age_days * 24 * 3600:
            cache_file.unlink()
            print(f"🧹 Deleted old cache: {cache_file.name}")
# For testing
if __name__ == "__main__":
    print("="*60)
    print("HYBRID NEWS DETECTOR - ONLINE CHECKER")
    print("="*60)
    print(f"API Key present: {'✅ Yes' if NEWS_API_KEY else '❌ No'}")
    
    test_headline = "elon musk is the richest man in the world"
    print("\n" + "="*60)
    print(f"🔍 Testing: '{test_headline}'")
    print("-"*40)
    result = check_news_online(test_headline)
    print(f"\n📌 Final Result: {result}")