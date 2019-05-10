import json
import random
import boto3


def predict_handler(event, context):
    print(event)
    # Receive message from scraper service on the triggerPredict SNS topic:
    # inbound_message = event['Records'][0]['Sns']['Message']
    inbound_message = json.loads(event['Records'][0]['Sns']['Message'])
    image_id = inbound_message['image_id']
    phone = inbound_message['phone']
    
    # Obsolete: receive message from S3
    # s3_message = event['Records'][0]['s3']
    
    # Temporary: for testing purposes, bypass predict service and send message 
    # to downstream outbound_SMS service on the "dlresult topic".
    # In production, the actual predict service should use this logic to write
    # to the dlresult topic:
    outbound_message = {'phone': phone,
                        'prediction': random.randint(0, 10)}

    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:245636212397:dlresult',    
        Message=json.dumps({'default': json.dumps(outbound_message)}),
        MessageStructure='json'
    )
    
    return outbound_message
