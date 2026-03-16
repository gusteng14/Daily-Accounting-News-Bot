import os
import sys
import datetime
import json
from bot.news_fetcher import fetch_all_daily_news
from bot.facebook_poster import post_to_facebook
from bot.image_generator import create_headline_image

def main():
    print(f"--- Running Daily Accounting News Bot ({datetime.datetime.now()}) ---")
    
    # Load previously posted URLs to avoid duplicates
    posted_urls_file = "posted_urls.json"
    posted_urls = []
    if os.path.exists(posted_urls_file):
        with open(posted_urls_file, "r") as f:
            try:
                posted_urls = json.load(f)
            except json.JSONDecodeError:
                posted_urls = []
                
    # 1. Fetch News
    print("Fetching recent news...")
    all_news_items = fetch_all_daily_news()
    
    # Filter out already posted news
    news_items = [item for item in all_news_items if item['link'] not in posted_urls]
    
    if not news_items:
        print("No new/unposted accounting/business news found.")
        return
        
    print(f"Found {len(news_items)} new unposted items.")
    
    # Limit to top 3 to avoid spamming the Facebook Page
    news_items = news_items[:3]
    
    # 2. Process and Post each item
    for idx, item in enumerate(news_items, 1):
        print(f"\nProcessing item {idx}/{len(news_items)}: {item['title']}")
        
        # A. Generate Image
        image_filename = f"news_image_{idx}.png"
        create_headline_image(item['title'], item['source'], image_filename)
        
        # B. Format Engaging Text
        # The prompt requested strictly headline, description, and source
        summary_text = item.get('summary', '').strip()
        if not summary_text or len(summary_text) < 10:
            summary_text = "Click the link below to read the full update and stay informed."
            
        message = (
            f"Headline: {item['title']}\n"
            f"Source: {item['source']}\n\n"
            f"Description: {summary_text}"
        )
        
        print(f"Drafted Message:\n{message}\n")
        
        # C. Post to Facebook with Image
        print(f"Saving as draft to Facebook Page...")
        success = post_to_facebook(message, image_path=image_filename)
        
        if success:
            print(f"Successfully posted item {idx}.")
            posted_urls.append(item['link'])
            # Keep the list size manageable (e.g., max 500 links)
            if len(posted_urls) > 500:
                posted_urls = posted_urls[-500:]
            # Save back to file
            with open(posted_urls_file, "w") as f:
                json.dump(posted_urls, f)
        else:
            print(f"Failed to post item {idx}.")
            
        # Clean up the generated image
        if os.path.exists(image_filename):
            os.remove(image_filename)
            
    print("\nDaily task completed.")

if __name__ == '__main__':
    main()
