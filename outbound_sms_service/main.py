import base64
import logging
import os
from urllib import parse, request
import json

TWILIO_SMS_URL = 'https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json'
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')


def lambda_handler(event, context):
    """Receive a message from predict service on the dlresult SNS topic"""
    # Insert Twilio Account SID into the REST API URL
    populated_url = TWILIO_SMS_URL.format(TWILIO_ACCOUNT_SID)

    event_message = json.loads(event['Records'][0]['Sns']['Message'])
    print (event_message)
    post_params = {'To': event_message['phone_number'],
                   'From': os.environ.get('from_number'),
                   'Body': event_message['body']}

    # Encode the parameters for Python's urllib
    data = parse.urlencode(post_params).encode()
    req = request.Request(populated_url)

    # Add authentication header to request based on Account SID + Auth Token
    authentication = '{}:{}'.format(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    base64string = base64.b64encode(authentication.encode('utf-8'))
    req.add_header('Authorization', 'Basic %s' % base64string.decode('ascii'))

    try:
        # Perform HTTP POST request
        with request.urlopen(req, data) as f:
            response = str(f.read().decode('utf-8'))
            logging.info(f"Twilio returned {response}")
    except Exception:
        logging.info('Something went wrong', exc_info=True)
