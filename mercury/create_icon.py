from PIL import Image, ImageDraw
import os

def create_simple_icon(size=64, color=(0, 120, 212), filename='app_icon.png'):
    # Create a new image with a white background
    image = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw a filled circle
    draw.ellipse([size//4, size//4, 3*size//4, 3*size//4], fill=color)
    
    # Save the image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, filename)
    image.save(icon_path)
    print(f"Icon saved at: {icon_path}")

if __name__ == "__main__":
    create_simple_icon()