import os
import sys
import datetime
import json
from bot.news_fetcher import fetch_all_daily_news
from bot.facebook_poster import post_to_facebook
from bot.image_generator import create_headline_image

def main():
    print(f"--- Running Daily Pet Care Tips Bot ({datetime.datetime.now()}) ---")
    
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
        print("No new/unposted pet care tips found.")
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
        # The prompt requested an engaging, short content without duplicated text
        title = item['title']
        source_suffix = f" - {item['source']}"
        if title.endswith(source_suffix):
            title = title[:-len(source_suffix)].strip()
            
        summary_text = item.get('summary', '').strip()
        if summary_text.endswith(item['source']):
            summary_text = summary_text[:-len(item['source'])].strip()
            
        # If the summary is too short or is identical to the title, use the title to avoid duplication
        if not summary_text or len(summary_text) < 10 or title.lower() in summary_text.lower() or summary_text.lower() in title.lower():
            summary_text = title
            
        message = (
            f"🚨 𝗕𝗥𝗘𝗔𝗞𝗜𝗡𝗚 𝗨𝗣𝗗𝗔𝗧𝗘 𝗙𝗥𝗢𝗠 {item['source'].upper()} 🚨\n\n"
            f"💡 𝗪𝗵𝗮𝘁 𝘆𝗼𝘂 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗸𝗻𝗼𝘄:\n"
            f"{summary_text}\n\n"
            f"Click the link below for more helpful tips to keep your furry friend happy and healthy!\n"
            f"{item['link']}\n\n"
            f"#PetCare #PetTips #AnimalWelfare #{item['source'].replace(' ', '')}"
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
