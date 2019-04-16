import json
import random

import boto3


def predict_handler(event, context):
    s3_message = event['Records'][0]['s3']

    message = {'prediction': random.randint(0, 10),
               'filename': s3_message['object']['key']}

    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:245636212397:dlresult',
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )

    return {'statusCode': 200, 'body': json.dumps(message)}
