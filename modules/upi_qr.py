"""
UPI QR Generator - Fixed price QR for each plan
UPI: kumaranil98787@axl
"""

import os
import io
import qrcode
from PIL import Image, ImageDraw, ImageFont
import urllib.parse

UPI_ID = os.getenv("UPI_ID", "kumaranil98787@axl").strip()
UPI_NAME = os.getenv("UPI_NAME", "OSINT Hunter Hub").strip()

def _q(s: str) -> str:
    return urllib.parse.quote(str(s), safe='')

def get_upi_link(amount: int, note: str = "OSINT Premium") -> str:
    if not UPI_ID:
        return ""
    return f"upi://pay?pa={_q(UPI_ID)}&pn={_q(UPI_NAME)}&am={amount}&cu=INR&tn={_q(note)}"

def generate_upi_qr(amount: int, plan_name: str = "Premium", note: str = "") -> io.BytesIO:
    """
    Generate UPI QR code with fixed price
    Returns BytesIO of PNG image
    """
    try:
        upi_link = get_upi_link(amount, note or f"OSINT {plan_name}")
        
        # Create QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_link)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        
        # Create final image with text
        # Add white background with plan info
        width, height = qr_img.size
        # Add extra height for text
        extra_height = 120
        final_img = Image.new('RGB', (width, height + extra_height), 'white')
        final_img.paste(qr_img, (0, 0))
        
        draw = ImageDraw.Draw(final_img)
        
        # Try to load font, fallback to default
        try:
            # Try to use a better font if available
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            try:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            except:
                font_large = None
                font_small = None
        
        # Add text
        text_y = height + 10
        try:
            draw.text((10, text_y), f"{plan_name} - ₹{amount}", fill="black", font=font_large)
            draw.text((10, text_y + 30), f"UPI: {UPI_ID}", fill="black", font=font_small)
            draw.text((10, text_y + 55), f"Scan to Pay - Fixed Price", fill="black", font=font_small)
            draw.text((10, text_y + 80), f"@{UPI_NAME}", fill="gray", font=font_small)
        except Exception as e:
            print(f"QR text draw failed: {e}")
            # Fallback without font
            draw.text((10, text_y), f"{plan_name} - Rs.{amount}", fill="black")
            draw.text((10, text_y + 25), f"UPI: {UPI_ID}", fill="black")
        
        # Save to BytesIO
        bio = io.BytesIO()
        final_img.save(bio, 'PNG')
        bio.seek(0)
        return bio
        
    except Exception as e:
        print(f"QR generation failed: {e}")
        # Return None or create simple QR without text
        try:
            upi_link = get_upi_link(amount, plan_name)
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(upi_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            bio = io.BytesIO()
            img.save(bio, 'PNG')
            bio.seek(0)
            return bio
        except Exception as e2:
            print(f"Simple QR also failed: {e2}")
            return None

def generate_qr_file(amount: int, plan_name: str, filepath: str) -> bool:
    """Generate QR and save to file"""
    try:
        bio = generate_upi_qr(amount, plan_name)
        if bio:
            with open(filepath, 'wb') as f:
                f.write(bio.getvalue())
            return True
        return False
    except Exception as e:
        print(f"QR file save failed: {e}")
        return False
