from pyzbar.pyzbar import decode
from PIL import Image
from typing import Optional
import os

def scan_it(qr_path: str) -> Optional[str]:
    """
    Scan a QR code image and return its decoded content.
    
    Args:
        qr_path: Path to the QR code image file
        
    Returns:
        Decoded QR code content or None if scanning fails
        
    Raises:
        FileNotFoundError: If the image file doesn't exist
        ValueError: If no QR code is found in the image
    """
    try:
        if not os.path.exists(qr_path):
            raise FileNotFoundError(f"QR code image not found: {qr_path}")
            
        img = Image.open(qr_path)
        result = decode(img)
        
        if not result:
            raise ValueError("No QR code found in image")
            
        return result[0][0].decode('utf-8')
        
    except Exception as e:
        print(f"Error scanning QR code: {str(e)}")
        return None