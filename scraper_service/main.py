# Original Scraper

from datetime import datetime
from time import sleep
from botocore.vendored import requests
from fake_useragent import UserAgent
import boto3
import json


def make_request():
    url = 'http://cdn.shakeshack.com/camera.jpg'
    headers = {'user-agent': UserAgent().random}
    r = requests.get(url, stream=True, headers=headers)
    if r.headers['content-length'] == '0':
        raise ValueError('No image was loaded, trying again...')
    else:
        return r


def scrape_handler(event, context):
    # Temp oscar work 5/4
    # only works if you trigger this function with a text message;
    # need to handle the other use case:
    event_message = json.loads(event['Records'][0]['Sns']['Message'])
    # event_message = event['Records'][0]['Sns']['Message']

    phone_raw = event_message['from']
    phone = phone_raw[-10:]

    # Image filename:
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime('%Y-%m-%d_%H%M_')
    filename = f'shackcam/{timestamp_str}' + phone + '.jpg'

    # Try 3 times to load an image
    fail_count = 0
    for x in range(0, 2):
        try:
            r = make_request()
        except ValueError as err:
            print(err)
            fail_count += 1
            sleep(1)
            pass

    # Upload image to S3
    if fail_count >= 2:
        # If shack cam is failing, just send an old image to S3
        s3 = boto3.resource('s3')
        copy_source = {'Bucket': 'deepshack', 'Key': 'samples/s_test.jpg'}
        bucket = s3.Bucket('deepshack')
        bucket.copy(copy_source, filename)

    else:
        # Actually scrape the image if shack cam is working
        session = boto3.Session()
        s3 = session.resource('s3')
        bucket_name = 'deepshack'
        bucket = s3.Bucket(bucket_name)

        r.raw.decode_content = True
        bucket.upload_fileobj(r.raw, filename)

    return {
        'filename': filename
    }
