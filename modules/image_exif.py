"""
Tool 5: Image EXIF Forensics - OSINT
Extracts EXIF metadata from images: GPS, camera, date, software, etc.
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
from typing import Dict, Any, Optional, Tuple
import datetime

def get_exif_data(image_path: str) -> Dict[str, Any]:
    """Extract raw EXIF data"""
    try:
        img = Image.open(image_path)
        exif_data = {}
        
        info = img._getexif()
        if info is None:
            return {"ok": False, "error": "No EXIF data found - image may be stripped or screenshot"}

        for tag_id, value in info.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_data[tag] = value

        return {"ok": True, "raw": exif_data, "format": img.format, "size": img.size, "mode": img.mode}
    except Exception as e:
        return {"ok": False, "error": f"EXIF read error: {str(e)}"}

def get_gps_info(exif_data: Dict) -> Optional[Dict[str, Any]]:
    """Extract GPS info from EXIF"""
    try:
        gps_info = exif_data.get("GPSInfo")
        if not gps_info:
            return None

        gps_data = {}
        for key in gps_info.keys():
            decode = GPSTAGS.get(key, key)
            gps_data[decode] = gps_info[key]

        # Convert GPS coordinates
        def convert_to_degrees(value):
            d = float(value[0])
            m = float(value[1])
            s = float(value[2])
            return d + (m / 60.0) + (s / 3600.0)

        lat = None
        lon = None

        if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
            lat = convert_to_degrees(gps_data["GPSLatitude"])
            if gps_data["GPSLatitudeRef"] != "N":
                lat = -lat

        if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
            lon = convert_to_degrees(gps_data["GPSLongitude"])
            if gps_data["GPSLongitudeRef"] != "E":
                lon = -lon

        if lat is not None and lon is not None:
            return {
                "latitude": lat,
                "longitude": lon,
                "lat_ref": gps_data.get("GPSLatitudeRef"),
                "lon_ref": gps_data.get("GPSLongitudeRef"),
                "altitude": gps_data.get("GPSAltitude"),
                "google_maps": f"https://www.google.com/maps?q={lat},{lon}",
                "osm": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}",
                "raw": gps_data
            }
        return {"raw": gps_data}
    except Exception as e:
        return {"error": str(e)}

def analyze_exif(image_path: str) -> Dict[str, Any]:
    """Full EXIF analysis - user friendly"""
    result = get_exif_data(image_path)
    if not result.get("ok"):
        return result

    raw = result.get("raw", {})
    
    # Extract important fields
    analysis = {
        "ok": True,
        "file": os.path.basename(image_path),
        "format": result.get("format"),
        "size": result.get("size"),
        "mode": result.get("mode"),
        "camera_make": raw.get("Make"),
        "camera_model": raw.get("Model"),
        "software": raw.get("Software"),
        "date_time": str(raw.get("DateTime")) if raw.get("DateTime") else None,
        "date_time_original": str(raw.get("DateTimeOriginal")) if raw.get("DateTimeOriginal") else None,
        "date_time_digitized": str(raw.get("DateTimeDigitized")) if raw.get("DateTimeDigitized") else None,
        "artist": raw.get("Artist"),
        "copyright": raw.get("Copyright"),
        "exposure_time": str(raw.get("ExposureTime")) if raw.get("ExposureTime") else None,
        "f_number": str(raw.get("FNumber")) if raw.get("FNumber") else None,
        "iso": raw.get("ISOSpeedRatings"),
        "focal_length": str(raw.get("FocalLength")) if raw.get("FocalLength") else None,
        "lens_model": raw.get("LensModel"),
        "image_width": raw.get("ExifImageWidth") or raw.get("ImageWidth"),
        "image_height": raw.get("ExifImageHeight") or raw.get("ImageLength"),
        "orientation": raw.get("Orientation"),
    }

    # GPS
    gps = get_gps_info(raw)
    analysis["gps"] = gps
    analysis["has_gps"] = bool(gps and "latitude" in gps)

    # Security / Forensics checks
    warnings = []
    if raw.get("Software"):
        sw = str(raw.get("Software")).lower()
        if "photoshop" in sw or "gimp" in sw or "lightroom" in sw:
            warnings.append(f"⚠️ Edited with {raw.get('Software')} - image may be manipulated")
    
    if not analysis["has_gps"] and analysis["camera_make"]:
        warnings.append("ℹ️ No GPS - location stripped or disabled, but camera info exists")
    
    if not raw.get("DateTimeOriginal") and raw.get("DateTime"):
        warnings.append("ℹ️ Original date missing, only file date available")

    if analysis["software"] and "screenshot" in str(analysis["software"]).lower():
        warnings.append("ℹ️ Appears to be a screenshot - limited EXIF")

    analysis["warnings"] = warnings
    analysis["total_exif_tags"] = len(raw)
    analysis["raw_exif"] = {k: str(v)[:500] for k, v in raw.items()}  # truncated for display

    return analysis

def exif_to_text(analysis: Dict[str, Any]) -> str:
    """Convert analysis to readable text for Telegram"""
    if not analysis.get("ok"):
        return f"❌ {analysis.get('error')}"

    txt = f"📸 <b>EXIF Forensics: {analysis.get('file')}</b>\n\n"
    txt += f"📐 <b>Format:</b> {analysis.get('format')} | Size: {analysis.get('size')} | Mode: {analysis.get('mode')}\n"
    txt += f"🏷️ <b>Total EXIF tags:</b> {analysis.get('total_exif_tags')}\n\n"

    txt += f"📷 <b>Camera:</b>\n"
    txt += f"• Make: {analysis.get('camera_make') or 'N/A'}\n"
    txt += f"• Model: {analysis.get('camera_model') or 'N/A'}\n"
    txt += f"• Lens: {analysis.get('lens_model') or 'N/A'}\n"
    txt += f"• Software: {analysis.get('software') or 'N/A'}\n\n"

    txt += f"📅 <b>Date/Time:</b>\n"
    txt += f"• Original: {analysis.get('date_time_original') or 'N/A'}\n"
    txt += f"• Digitized: {analysis.get('date_time_digitized') or 'N/A'}\n"
    txt += f"• File Date: {analysis.get('date_time') or 'N/A'}\n\n"

    txt += f"🔧 <b>Settings:</b>\n"
    txt += f"• ISO: {analysis.get('iso') or 'N/A'} | F: {analysis.get('f_number') or 'N/A'} | Exposure: {analysis.get('exposure_time') or 'N/A'}\n"
    txt += f"• Focal: {analysis.get('focal_length') or 'N/A'} | Width: {analysis.get('image_width') or 'N/A'} | Height: {analysis.get('image_height') or 'N/A'}\n\n"

    gps = analysis.get("gps")
    if analysis.get("has_gps") and gps:
        txt += f"📍 <b>GPS Location FOUND:</b>\n"
        txt += f"• Lat: {gps.get('latitude')}\n"
        txt += f"• Lon: {gps.get('longitude')}\n"
        txt += f"• Maps: {gps.get('google_maps')}\n"
        txt += f"• OSM: {gps.get('osm')}\n\n"
    else:
        txt += f"📍 <b>GPS:</b> Not found (location stripped or no GPS)\n\n"

    if analysis.get("artist"):
        txt += f"👤 <b>Artist:</b> {analysis.get('artist')}\n"
    if analysis.get("copyright"):
        txt += f"©️ <b>Copyright:</b> {analysis.get('copyright')}\n"

    if analysis.get("warnings"):
        txt += f"\n⚠️ <b>Forensics Notes:</b>\n"
        for w in analysis.get("warnings"):
            txt += f"• {w}\n"

    return txt
