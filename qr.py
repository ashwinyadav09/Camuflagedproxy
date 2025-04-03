from pyzbar.pyzbar import decode
from PIL import Image
import os

def scan_it(qr):
    try:
        # Ensure the file path is absolute and exists
        qr_path = os.path.abspath(qr)
        if not os.path.exists(qr_path):
            print(f"Error: QR file '{qr_path}' does not exist")
            return None
        img = Image.open(qr_path)
        result = decode(img)
        if result:
            qr_data = result[0][0].decode('utf-8')
            print(f"Decoded QR code: {qr_data}")
            return qr_data
        else:
            print(f"Error: No QR code found in '{qr_path}'")
            return None
    except FileNotFoundError:
        print(f"Error: QR image file '{qr}' not found")
        return None
    except Exception as e:
        print(f"Error decoding QR code from '{qr}': {e}")
        return None