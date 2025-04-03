from pyzbar.pyzbar import decode
from PIL import Image

def scan_it(qr):
    try:
        img = Image.open(qr)
        result = decode(img)
        if result:
            return result[0][0].decode('utf-8')
        else:
            raise ValueError("No QR code found in the image")
    except FileNotFoundError:
        print(f"Error: QR image file '{qr}' not found")
        return None
    except Exception as e:
        print(f"Error decoding QR code: {e}")
        return None