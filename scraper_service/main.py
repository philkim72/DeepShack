import shutil
from time import time
from datetime import datetime

import requests
from fake_useragent import UserAgent


def scrape_handler():
   
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d_%H%M-%S")

    url = f"http://cdn.shakeshack.com/camera.jpg"
    filename = f"{timestamp_str}.jpg"

    headers = {'user-agent': UserAgent().random}
    r = requests.get(url, stream=True, headers=headers)

    if r.status_code == 200:
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    return r.status_code
