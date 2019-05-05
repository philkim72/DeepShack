from __future__ import print_function
import json
import boto3

def lambda_handler(event, context):
    # Process message from the Lex Service:
    print("Processing message from Twilio")
    
    message = {
        'type': "twilio_inbound",
        'from': event["From"],
        'body': event["Body"],
    }
    
    text_content = event["Body"]
    
    # TODO (Phil):
    # if text_content contains a keyword suggesting the user wants to scrape, kick off the scraper
    # otherwise, respond to the user with a clarifying question
    
    # Scrape:
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:245636212397:lexMessage',   
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )
    # print("Received event: " + str(event))
    print("Important info: ", message)
    return '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
          '<Response><Message>Hello from DeepShack! We are calculating your time-to-burger. Hang tight...</Message></Response>'