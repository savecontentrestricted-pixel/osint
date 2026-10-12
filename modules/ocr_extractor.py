"""
OCR Extractor - Slim version - optional easyocr/pytesseract
If libs missing, returns nice error
"""

def ocr_image(image_path, lang="en"):
    try:
        import easyocr
        reader = easyocr.Reader(['en', 'hi'] if lang == 'hi' else ['en'], gpu=False)
        result = reader.readtext(image_path, detail=0)
        text = "\n".join(result)
        return {"ok": True, "text": text, "method": "easyocr", "chars": len(text)}
    except ImportError:
        pass
    except Exception:
        pass

    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='eng+hin' if lang == 'hi' else 'eng')
        return {"ok": True, "text": text, "method": "pytesseract", "chars": len(text)}
    except ImportError:
        return {"ok": False, "error": "OCR requires easyocr or pytesseract. On Render slim, OCR disabled to save RAM. Install locally: pip install pytesseract + tesseract-ocr binary"}
    except Exception as e:
        return {"ok": False, "error": f"OCR error: {str(e)[:200]}"}
