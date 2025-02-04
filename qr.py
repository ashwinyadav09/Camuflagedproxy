from pyzbar.pyzbar import decode
from PIL import Image

def scan_it(qr):
    try:
        img = Image.open(qr)
        result = decode(img)

        if not result:  # If no QR code is detected
            print("Error: No QR code detected or QR is expired.")
            return None  # Return None instead of crashing

        return result[0].data.decode('utf-8')  # Corrected decoding
    except Exception as e:
        print(f"Error scanning QR: {e}")
        return None  # Return None on failure
