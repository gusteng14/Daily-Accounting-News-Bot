import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

def create_headline_image(headline, source, output_filename="headline_image.png"):
    """
    Generates a simple, clean image with the news headline and source.
    """
    # 1. Create a background canvas (1080x1080 for Facebook/Instagram square)
    width = 1080
    height = 1080
    bg_color = (20, 30, 48) # Dark blue/slate background
    text_color = (255, 255, 255) # White text
    accent_color = (0, 204, 153) # Teal green accent for accounting feel
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # 2. Add some simple design elements
    # Top border line
    draw.rectangle([(50, 50), (width - 50, 60)], fill=accent_color)
    
    # 3. Load fonts (using default PIL font since we can't guarantee system fonts)
    # In a production environment, you would download a TTF file like Roboto or Inter
    try:
        # Try to use a common Windows font if available
        title_font = ImageFont.truetype("arialbd.ttf", 60)
        source_font = ImageFont.truetype("arial.ttf", 40)
        brand_font = ImageFont.truetype("arialbd.ttf", 35)
    except IOError:
        # Fallback to default, though it will be small
        title_font = ImageFont.load_default()
        source_font = ImageFont.load_default()
        brand_font = ImageFont.load_default()
        
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
    brand_text = "Philippine Accounting & Business News"
    draw.text((100, height - 150), brand_text, font=brand_font, fill=(150, 150, 150))
    
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
