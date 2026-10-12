"""
OCR Extractor - Image to Text
Uses EasyOCR + Pytesseract fallback, 100% working offline
"""

from PIL import Image
import os
from typing import Dict, Any

def ocr_image(image_path: str, lang: str = "en") -> Dict[str, Any]:
    """
    Extract text from image using OCR
    Supports Hindi + English
    """
    try:
        # Try EasyOCR first (more accurate)
        try:
            import easyocr
            reader = easyocr.Reader(['en', 'hi'] if lang == 'hi' else ['en'], gpu=False)
            result = reader.readtext(image_path, detail=0)
            text = "\n".join(result)
            return {"ok": True, "text": text, "method": "easyocr", "chars": len(text)}
        except ImportError:
            pass
        except Exception as e:
            # Fallback to pytesseract
            pass

        # Fallback to pytesseract
        try:
            import pytesseract
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang='eng+hin' if lang == 'hi' else 'eng')
            return {"ok": True, "text": text, "method": "pytesseract", "chars": len(text)}
        except ImportError:
            return {"ok": False, "error": "OCR lib not installed. Install: pip install easyocr OR pytesseract + tesseract-ocr"}
        except Exception as e:
            return {"ok": False, "error": f"OCR error: {str(e)}"}

    except Exception as e:
        return {"ok": False, "error": f"OCR failed: {str(e)}"}

def ocr_to_text_file(text: str, output_path: str):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
