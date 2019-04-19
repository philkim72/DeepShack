import shutil
from time import time

import requests
from fake_useragent import UserAgent


def scrape_handler():
    now = int(time())

    url = f"http://cdn.shakeshack.com/camera.jpg?{now}"
    filename = f"{now}.jpg"

    headers = {'user-agent': UserAgent().random}
    r = requests.get(url, stream=True, headers=headers)

    if r.status_code == 200:
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    return r.status_code
