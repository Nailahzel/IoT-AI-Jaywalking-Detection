import requests
import base64

SERVER_URL = "http://13.48.46.60/upload_event.php"

img_b64 = base64.b64encode(b"hello").decode()

payload = {
    "event_type": "test",
    "timestamp": "now",
    "location": "camera",
    "zebra_found": 1,
    "person_count": 1,
    "image_base64": img_b64
}

r = requests.post(SERVER_URL, json=payload)
print(r.text)
