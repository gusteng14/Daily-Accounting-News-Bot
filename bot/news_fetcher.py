import requests
from bs4 import BeautifulSoup
import feedparser
import datetime
from urllib.parse import urljoin, quote
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_google_news_rss():
    """Fetches news from Google News RSS using specific queries for Philippine accounting/gov/firms."""
    # Query targets reliable pet care sources
    query = '("pet care" OR "dog care" OR "cat care" OR "pet health") (site:avma.org OR site:aspca.org OR site:petmd.com OR site:akc.org)'
    encoded_query = quote(query)
    rss_url = f'https://news.google.com/rss/search?q={encoded_query}&hl=en-PH&gl=PH&ceid=PH:en'
    
    feed = feedparser.parse(rss_url)
    news_items = []
    
    # Get today's date to filter out old news
    today = datetime.datetime.now().date()
    start_date = today - datetime.timedelta(days=7)
    
    for entry in feed.entries:
        # Check if the news is from the last 1-3 months
        try:
            # RSS format usually provides published_parsed
            pub_date = datetime.datetime(*entry.published_parsed[:6]).date()
            if pub_date >= start_date:
                # Clean up HTML tags from RSS summary if present
                raw_summary = entry.summary if hasattr(entry, 'summary') else ""
                clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text() if raw_summary else ""
                
                # Extract first complete sentence to avoid '...'
                clean_text = clean_summary.replace('...', '')
                sentences = re.split(r'(?<=[.!?])\s+', clean_text)
                final_summary = "Read the full update from the official source."
                for s in sentences:
                    if len(s) > 30:
                        final_summary = s.strip()
                        if not final_summary.endswith(('.', '!', '?')):
                            final_summary += '.'
                        break
                
                news_items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': final_summary,
                    'source': entry.source.title if hasattr(entry, 'source') else 'Google News',
                    'date': entry.published
                })
        except Exception:
            # If parsing date fails, just include it (we can limit the total number later)
            raw_summary = entry.summary if hasattr(entry, 'summary') else ""
            clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text() if raw_summary else ""
            
            clean_text = clean_summary.replace('...', '')
            sentences = re.split(r'(?<=[.!?])\s+', clean_text)
            final_summary = "Read the full update from the official source."
            for s in sentences:
                if len(s) > 30:
                    final_summary = s.strip()
                    if not final_summary.endswith(('.', '!', '?')):
                        final_summary += '.'
                    break
            
            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'summary': final_summary,
                'source': entry.source.title if hasattr(entry, 'source') else 'Google News',
                'date': entry.published if hasattr(entry, 'published') else str(today)
            })
            
    return news_items

def fetch_all_daily_news():
    """Aggregates news from all sources."""
    print("Fetching pet care tips from Google News RSS...")
    all_news = fetch_google_news_rss()
        
    # Remove duplicates based on link and title similarity
    unique_news = []
    seen_links = set()
    
    for item in all_news:
        if item['link'] not in seen_links:
            unique_news.append(item)
            seen_links.add(item['link'])
            
    # Return the most recent/relevant ones (limit to top 5 for daily posting)
    return unique_news[:5]

if __name__ == '__main__':
    news = fetch_all_daily_news()
    for n in news:
        print(f"- {n['title']} ({n['source']}) -> {n['link']}")
