import json
import logging
from datetime import datetime
from time import sleep

from pytz import timezone
from botocore.vendored import requests
import boto3
from fake_useragent import UserAgent

URL = 'http://cdn.shakeshack.com/camera.jpg'
PREDICT_TOPIC_ARN = 'arn:aws:sns:us-east-1:245636212397:triggerPredict'
SMS_TOPIC_ARN = 'arn:aws:sns:us-east-1:245636212397:triggerSMS'
S3_BUCKET = 'deepshack'

logging.getLogger().setLevel(logging.INFO)


def make_request():
    """Sends GET request to the ShackCam and returns response object"""
    headers = {'user-agent': UserAgent().random}
    r = requests.get(URL, stream=True, headers=headers)
    if r.headers['content-length'] == '0':
        raise ValueError('No image was loaded, trying again...')
    else:
        return r


def publish_message(message, topic_arn):
    """Publishes a message to SNS topic"""
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )
    logging.info(response)


def scrape_handler(event, context):
    """
    Main function that gets called by Lambda. Subscribes to a message topic,
    triggerPredict, scrapes an image, saves to AWS S3, and then publishes
    messages to triggerPredict and triggerSMS
    """

    # Receive message from upstream service
    event_message = event['Records'][0]['Sns']['Message']
    phone_number = event_message['phone_number'].split("B")[-1]

    timestamp = datetime.now(timezone('EST'))
    timestamp_str = timestamp.strftime('%Y_%m_%d_%H%M')
    filename = f'shackcam/{timestamp_str}.jpg'

    outbound_message = {'filename': filename, 'phone_number': phone_number}

    # Try 3 times to scrape an image
    fail_count = 0
    for _ in range(0, 2):
        try:
            # Scrape
            r = make_request()
            r.raw.decode_content = True

            # Upload to S3
            session = boto3.Session()
            s3 = session.resource('s3')
            bucket = s3.Bucket(S3_BUCKET)
            bucket.upload_fileobj(r.raw, filename)

            # Publish message to downstream services
            publish_message(outbound_message, PREDICT_TOPIC_ARN)
            outbound_message['body'] = (
                "Good news! DeepShack is on your way."
                "Image was scraped from ShackCam and saved on AWS S3."
                "predict_trigger_service on Lambda will be called next"
            )
            publish_message(outbound_message, SMS_TOPIC_ARN)

        except ValueError as err:
            logging.info(err)
            fail_count += 1
            sleep(1)

        # Publish failed message to downstream services
        outbound_message['body'] = (
                "Bad news:( Image was not successfully scraped from ShackCam."
                "No Shake Shack for you today."
        )
        publish_message(outbound_message, SMS_TOPIC_ARN)
