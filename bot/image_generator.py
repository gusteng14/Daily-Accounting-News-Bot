import os
import textwrap
import urllib.request
from PIL import Image, ImageDraw, ImageFont

def get_font(size, bold=False):
    font_url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf" if bold else "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
    font_name = "Roboto-Bold.ttf" if bold else "Roboto-Regular.ttf"
    
    # Store font in the same directory as this script
    font_path = os.path.join(os.path.dirname(__file__), font_name)
    
    if not os.path.exists(font_path):
        try:
            print(f"Downloading font {font_name}...")
            urllib.request.urlretrieve(font_url, font_path)
        except Exception as e:
            print(f"Failed to download font: {e}")
            return ImageFont.load_default()
            
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def create_headline_image(headline, source, output_filename="headline_image.png"):
    """
    Generates a simple, clean image with the news headline and source.
    """
    # 1. Create a background canvas (1080x1080 for Facebook/Instagram square)
    width = 1080
    height = 1080
    bg_color = (255, 248, 220) # Light Pastel Yellow/Cornsilk
    text_color = (40, 40, 40) # Dark gray text for readability
    accent_color = (255, 153, 153) # Pastel pink accent
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # 2. Add some simple design elements
    # Top border line
    draw.rectangle([(50, 50), (width - 50, 60)], fill=accent_color)
    
    title_font = get_font(60, bold=True)
    source_font = get_font(40, bold=False)
    brand_font = get_font(35, bold=True)
        
    # 4. Draw the source tag above the headline
    source_text = f"SOURCE: {source.upper()}"
    draw.text((100, 200), source_text, font=source_font, fill=accent_color)
    
    # 5. Wrap and draw the headline
    # textwrap breaks the long headline into multiple lines
    max_chars_per_line = 30
    wrapped_headline = textwrap.wrap(headline, width=max_chars_per_line)
    
    y_text = 300
    for line in wrapped_headline:
        draw.text((100, y_text), line, font=title_font, fill=text_color)
        y_text += 80 # line height
        
    # 6. Draw branding at the bottom
    brand_text = "Daily Pet Care Tips"
    draw.text((100, height - 150), brand_text, font=brand_font, fill=(100, 100, 100))
    
    # Bottom border line
    draw.rectangle([(50, height - 60), (width - 50, height - 50)], fill=accent_color)
    
    # 7. Save the image
    img.save(output_filename)
    return output_filename

if __name__ == '__main__':
    # Test the image generation
    create_headline_image(
        "BIR issues latest revenue regulations on withholding tax for online sellers",
        "Bureau of Internal Revenue",
        "test_image.png"
    )
    print("Test image generated.")
