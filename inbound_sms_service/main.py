from __future__ import print_function
import json
import boto3

def lambda_handler(event, context):
    #
    # Extract phone number from text and compose outbound message
    outbound_message = {'from': event["From"]}
    
    # TODO (Phil)
    # Process the SMS content from the user
    # - if text_content contains a keyword suggesting the user wants to scrape, kick off the scraper
    # - otherwise, respond to the user with a clarifying question
    text_content = event["Body"]
    
    # Send outbound_message to scraper service on lexMessage topic
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:245636212397:lexMessage',   
        Message=json.dumps({'default': json.dumps(outbound_message)}),
        MessageStructure='json'
    )
    # print("Received event: " + str(event))
    return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
          '<Response><Message>Hello from DeepShack! We are calculating your time-to-burger. Hang tight...</Message></Response>'