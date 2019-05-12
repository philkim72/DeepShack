import json
import logging

import boto3

logging.getLogger().setLevel(logging.INFO)

SMS_TOPIC_ARN = 'arn:aws:sns:us-east-1:245636212397:triggerSMS'


def publish_message(message, topic_arn):
    """Publishes a message to SNS topic"""
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )
    logging.info(response)


def predict_trigger_handler(event, context):
    """Subscribes to triggerPredict SNS topic and triggers"""
    # inbound_message = event['Records'][0]['Sns']['Message']
    inbound_message = json.loads(event['Records'][0]['Sns']['Message'])
    filename = inbound_message['filename']
    phone_number = inbound_message['phone_number']

    outbound_message = {'filename': filename, 'phone_number': phone_number}
    outbound_message['body'] = (
                "We are now spinning up an ECS instance. "
                "This machine will count the people in the Shack line. "
                "This could take a few minutes."
    )
    publish_message(outbound_message, SMS_TOPIC_ARN)

    ecs = boto3.client('ecs')
    response = ecs.run_task(
        cluster='cluster2',
        launchType='FARGATE',
        taskDefinition='predict_task2',
        count=1,
        overrides={'containerOverrides': [{
            'name': 'deepshack_predict',
            'environment': [{'name': 'FILENAME', 'value': filename},
                            {'name': 'PHONE_NUMBER', 'value': phone_number}]
        }]},
        platformVersion='LATEST',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': ['subnet-024f6febf0181b1df'],
                'assignPublicIp': 'ENABLED'
            }
        }
    )

    response = json.dumps(response, sort_keys=True, default=str)
    logging.info(response)
