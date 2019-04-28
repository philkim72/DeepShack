import json
import boto3

# Initialize SNS client for Ireland region
session = boto3.Session(
    region_name="us-east-1"
)
sns_client = session.client('sns')

def lambda_handler(event, context):

    event_message = json.load(event['Records'][0]['Sns']['Message'])
    pred = event_message['prediction']
    filename = event_message['filename']

    # Send SMS
    response = sns_client.publish(
        PhoneNumber="+1##########",
        Message='There are only '+str(pred)+' people in the line',
        MessageAttributes={
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': 'DeepShack'
            },
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': 'Promotional'
            }
        }
    )

    return 'OK'
