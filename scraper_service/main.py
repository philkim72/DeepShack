from datetime import datetime
from time import sleep
from botocore.vendored import requests
from fake_useragent import UserAgent
import boto3


def make_request():
    url = 'http://cdn.shakeshack.com/camera.jpg'
    headers = {'user-agent': UserAgent().random}
    r = requests.get(url, stream=True, headers=headers)
    if r.headers['content-length'] == '0':
        raise ValueError('No image was loaded, trying again...')
    else:
        return r


def scrape_handler(event, context):
    session = boto3.Session()
    s3 = session.resource('s3')

    # Try 3 times to load an image
    for x in range(0, 3):
        try:
            r = make_request()
        except ValueError as err:
            print(err)
            sleep(5)
            pass

    # Create image filename
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime('%Y-%m-%d_%H%M-%S')
    filename = f'shackcam/{timestamp_str}.jpg'

    # Upload image to S3
    bucket_name = 'deepshack'
    bucket = s3.Bucket(bucket_name)
    r.raw.decode_content = True
    bucket.upload_fileobj(r.raw, filename)

    return {
        'image size (bytes)': r.headers['content-length'],
        'filename': filename
    }
