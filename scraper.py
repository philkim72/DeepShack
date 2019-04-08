import shutil
from random import randint
from time import sleep, time

import requests
from fake_useragent import UserAgent


def download_img(url, filename, agent):
    headers = {'user-agent': agent}
    r = requests.get(url, stream=True, headers=headers)

    if r.status_code == 200:
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    return r.status_code


def main():
    ua = UserAgent()
    while True:
        sleep(randint(1, 5))
        now = int(time())

        url = f"http://cdn.shakeshack.com/camera.jpg?{now}"
        filename = f"shakeshack/shackcam_{now}.jpg"

        print(download_img(url, filename, ua.random))


if __name__ == '__main__':
    main()
