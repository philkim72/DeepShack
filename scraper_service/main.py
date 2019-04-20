import shutil
from time import time

import requests
from fake_useragent import UserAgent


def scrape_handler():
   
    timestamp = datetime.now()
    timestampString = str(timestamp.date()) + "_" + str(timestamp.hour).zfill(2) + "-" + str(timestamp.minute).zfill(2) \
        + "-" + str(timestamp.second).zfill(2)

    url = f"http://cdn.shakeshack.com/camera.jpg"
    filename = f"{timestampString}.jpg"

    headers = {'user-agent': UserAgent().random}
    r = requests.get(url, stream=True, headers=headers)

    if r.status_code == 200:
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    return r.status_code
