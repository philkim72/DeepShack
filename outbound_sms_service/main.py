import base64
import json
import os
from urllib import request, parse

from boto3 import resource
# from boto3.dynamodb.conditions import Key, Attr

TWILIO_SMS_URL = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

# The boto3 dynamoDB resource
dynamodb_resource = resource('dynamodb')
table = dynamodb_resource.Table('user_image')


def lambda_handler(event, context):

    # Receive message from predict service on the dlresult SNS topic:
    # event_message = event['Records'][0]['Sns']['Message']
    event_message = json.loads(event['Records'][0]['Sns']['Message'])

    to_number_raw = event_message['phone']
    to_number = "+" + to_number_raw

    from_number = os.environ.get("from_number")
    body = "There are " + str(event_message['prediction']) + \
        " people in line right now. Get the Double Shack!!"

    # insert Twilio Account SID into the REST API URL
    populated_url = TWILIO_SMS_URL.format(TWILIO_ACCOUNT_SID)
    post_params = {"To": to_number, "From": from_number, "Body": body}

    # encode the parameters for Python's urllib
    data = parse.urlencode(post_params).encode()
    req = request.Request(populated_url)

    # add authentication header to request based on Account SID + Auth Token
    authentication = "{}:{}".format(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    base64string = base64.b64encode(authentication.encode('utf-8'))
    req.add_header("Authorization", "Basic %s" % base64string.decode('ascii'))

    try:
        # perform HTTP POST request
        with request.urlopen(req, data) as f:
            print("Twilio returned {}".format(str(f.read().decode('utf-8'))))
    except Exception as e:
        # something went wrong!
        return e

    return "SMS sent successfully!"
