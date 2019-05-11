from __future__ import print_function
import json
import boto3
import logging

SMS_TOPIC_ARN = 'arn:aws:sns:us-east-1:245636212397:triggerSMS'
SCRAPE_TOPIC_ARN = 'arn:aws:sns:us-east-1:245636212397:triggerScrape'


def publish_message(message, topic_arn):
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )
    logging.info(response)


def lambda_handler(event, context):
    # Extract phone number from text and compose outbound message
    outbound_message = {'phone_number': "+" + event['From'].split("B")[-1]}
    message_content = event['Body'].strip()
    if message_content not in ('0', '1'):
        text_message = ("Hello from DeepShack!\n\n"
                        "DeepShack Menu:\n"
                        "0 - About the Service\n"
                        "1 - How long is the line at Shake Shack?")
        outbound_message['body'] = text_message
        publish_message(outbound_message, SMS_TOPIC_ARN)
    else:
        if message_content == '0':
            text_message = ("A Deep Learning application that estimates the "
                            "Shake Shack line using the live streaming "
                            "located at Madison Square Park. The application "
                            "is based on a decoupled microservice "
                            "architecture implemented using AWS ECS, Lambda, "
                            "SNS and Twilio SMS.")
            outbound_message['body'] = text_message
            publish_message(outbound_message, SMS_TOPIC_ARN)
        else == '1':
            publish_message(outbound_message, SCRAPE_TOPIC_ARN)
            text_message = ("Hello from DeepShack! We are calculating your "
                            "time-to-burger. Hang tight...")
            outbound_message['body'] = text_message
            publish_message(outbound_message, SMS_TOPIC_ARN)
