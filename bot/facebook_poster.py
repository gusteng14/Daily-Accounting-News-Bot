import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def post_to_facebook(message, link=None, image_path=None):
    """
    Posts a message, an optional link, and an optional image to a Facebook Page using the Graph API.
    Requires FB_PAGE_ID and FB_PAGE_ACCESS_TOKEN in the environment.
    """
    page_id = os.getenv('FB_PAGE_ID')
    access_token = os.getenv('FB_PAGE_ACCESS_TOKEN')
    
    if not page_id or not access_token or page_id == 'your_page_id_here':
        print("Error: Facebook Page ID or Access Token is missing or not configured in .env file.")
        return False
        
    if image_path and os.path.exists(image_path):
        # 1. Upload the photo as unpublished first
        url_photos = f"https://graph.facebook.com/v19.0/{page_id}/photos"
        
        payload_photo = {
            'access_token': access_token,
            'published': 'false'
        }
        
        try:
            with open(image_path, 'rb') as img:
                files = {'source': img}
                response_photo = requests.post(url_photos, data=payload_photo, files=files)
            
            response_photo.raise_for_status()
            photo_id = response_photo.json().get('id')
            
            # 2. Create the draft post attached with the photo
            url_feed = f"https://graph.facebook.com/v19.0/{page_id}/feed"
            full_message = f"{message}\n\nRead more: {link}" if link else message
            
            payload_feed = {
                'message': full_message,
                'access_token': access_token,
                'published': 'false',
                'unpublished_content_type': 'DRAFT',
                'attached_media': json.dumps([{"media_fbid": photo_id}])
            }
            
            response_feed = requests.post(url_feed, data=payload_feed)
            response_feed.raise_for_status()
            
            print(f"Successfully saved Draft with Photo to Facebook Page! Post ID: {response_feed.json().get('id')}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to post to Facebook. Error: {e}")
            if e.response is not None:
                print(f"Facebook Graph API Response: {e.response.text}")
            return False
    else:
        # Fallback to text link post if no image
        url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        
        payload = {
            'message': message,
            'access_token': access_token,
            'published': 'false',
            'unpublished_content_type': 'DRAFT'
        }
        
        if link:
            payload['link'] = link
            
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            print(f"Successfully posted text to Facebook Page! Post ID: {response.json().get('id')}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to post to Facebook. Error: {e}")
            if e.response is not None:
                print(f"Facebook Graph API Response: {e.response.text}")
            return False

if __name__ == '__main__':
    # Simple test
    # post_to_facebook("Test post from Daily Accounting News Bot.")
    pass
