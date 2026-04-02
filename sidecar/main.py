import sys
import easyocr
import json
from PIL import Image
import os

def perform_ocr(image_path, coords=None, languages=['ko', 'en']):
    """
    image_path: /path/to/image
    coords: [x, y, w, h] (pixels)
    """
    if not os.path.exists(image_path):
        return {"error": f"File not found: {image_path}"}

    try:
        reader = easyocr.Reader(languages)
        
        # Crop image if coords are provided
        if coords:
            x, y, w, h = coords
            img = Image.open(image_path)
            # Standard PIL crop takes (left, top, right, bottom)
            cropped_img = img.crop((x, y, x + w, y + h))
            # Save temporary for easyocr - or pass as array (easier with np array)
            # EasyOCR can take a path or numpy array. PIL to numpy:
            import numpy as np
            image_input = np.array(cropped_img)
        else:
            image_input = image_path
            
        results = reader.readtext(image_input)
        
        # Combine all recognized texts
        text = " ".join([res[1] for res in results])
        return {"text": text.strip()}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Expecting: python main.py <image_path> [x,y,w,h]
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image path provided"}))
        sys.exit(1)

    image_path = sys.argv[1]
    coords = None
    if len(sys.argv) > 2:
        try:
            coords = [int(v) for v in sys.argv[2].split(',')]
        except:
            pass
            
    result = perform_ocr(image_path, coords)
    print(json.dumps(result))
