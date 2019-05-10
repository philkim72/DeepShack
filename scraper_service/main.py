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
    
    # Receive message from inbound_SMS_service on the lexMessage SNS topic:
    event_message = json.loads(event['Records'][0]['Sns']['Message'])
    # event_message = event['Records'][0]['Sns']['Message']
    
    # Get phone number:
    phone_raw = event_message['from']
    phone = phone_raw.split("B")[-1]
    
    # Get image filename:
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime('%Y-%m-%d_%H%M_')
    filename = f'shackcam/{timestamp_str}' + phone + '.jpg'
    
    # Create message and send to predict_service_trigger on topic "triggerPredict"
    outbound_message = {'image_id': filename,
                        'phone': phone}
    
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:245636212397:triggerPredict',   
        Message=json.dumps({'default': json.dumps(outbound_message)}),
        MessageStructure='json'
    )
    
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
        # write_to_dynamo(filename, phone, 0)
        
    else:
        # Scrape the image if shack cam is working
        session = boto3.Session()
        s3 = session.resource('s3')
        bucket_name = 'deepshack'
        bucket = s3.Bucket(bucket_name)

        r.raw.decode_content = True
        bucket.upload_fileobj(r.raw, filename)
        # write_to_dynamo(filename, phone, 0)
        
    return outbound_message
