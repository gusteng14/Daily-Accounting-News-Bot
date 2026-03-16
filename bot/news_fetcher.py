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
    # Query targets specified agencies in the Philippines
    query = '("Bureau of Internal Revenue" OR BIR OR "Securities and Exchange Commission" OR "SEC Philippines" OR "Social Security System" OR SSS OR "Pag-IBIG" OR HDMF OR "Bangko Sentral ng Pilipinas" OR BSP) -basketball -NCAA -sports -PRC -"Professional Regulation Commission" location:Philippines'
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

def scrape_homepage_news(url, agency_name):
    """
    A generic scraper that tries to find recent news or press releases on a given homepage.
    It looks for common keywords in links like 'news', 'press-release', 'advisory', 'article'.
    """
    news_items = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Attempt to get meta description of the homepage for a generic summary
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        default_summary = meta_desc['content'] if meta_desc else "Latest updates from official sources."
        
        # Look for links that might represent news
        keywords = ['news', 'press-release', 'advisory', 'article', 'updates']
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True)
            
            # Simple heuristic: if the link text is long enough to be a title and URL has a keyword
            if len(text) > 25 and any(kw in href.lower() for kw in keywords):
                full_link = urljoin(url, href)
                # Avoid duplicates
                if not any(item['link'] == full_link for item in news_items):
                    # Try to fetch the actual article to get a better summary (optional, but requested for engaging content)
                    try:
                        art_resp = requests.get(full_link, headers=HEADERS, timeout=5)
                        art_soup = BeautifulSoup(art_resp.content, 'html.parser')
                        p_tags = art_soup.find_all('p')
                        # Get first substantive paragraph
                        article_summary = default_summary
                        for p in p_tags:
                            text = p.get_text(strip=True)
                            if len(text) > 50:
                                sentences = re.split(r'(?<=[.!?])\s+', text.replace('...', ''))
                                if sentences and len(sentences[0]) > 20:
                                    article_summary = sentences[0].strip()
                                    if not article_summary.endswith(('.', '!', '?')):
                                        article_summary += '.'
                                else:
                                    article_summary = text.strip() + '.'
                                break
                    except:
                        article_summary = default_summary

                    news_items.append({
                        'title': text,
                        'link': full_link,
                        'summary': article_summary,
                        'source': agency_name,
                        'date': str(datetime.datetime.now().date()) # Rough approximation for today
                    })
                    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        
    return news_items

def fetch_all_daily_news():
    """Aggregates news from all sources."""
    print("Fetching news from Google News RSS...")
    all_news = fetch_google_news_rss()
    
    # We can also attempt to scrape some official homepages directly as requested
    targets = [
        ('https://www.bir.gov.ph/', 'BIR'),
        ('https://www.sec.gov.ph/', 'SEC'),
        ('https://www.sss.gov.ph/', 'SSS'),
        ('https://www.pagibigfund.gov.ph/', 'Pag-IBIG'),
        ('https://www.bsp.gov.ph/', 'BSP')
    ]
    
    for url, name in targets:
        print(f"Attempting to scrape {name} homepage directly...")
        direct_news = scrape_homepage_news(url, name)
        # Limit to top 2 to not overwhelm
        all_news.extend(direct_news[:2])
        
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
