import json
import logging

import boto3

logging.getLogger().setLevel(logging.INFO)


def predict_trigger_handler(event, context):
    """Subscribes to triggerPredict SNS topic and triggers"""
    # inbound_message = event['Records'][0]['Sns']['Message']
    inbound_message = json.loads(event['Records'][0]['Sns']['Message'])
    filename = inbound_message['filename']
    phone_number = inbound_message['phone_number']

    ecs = boto3.client('ecs')
    response = ecs.run_task(
        cluster='cluster2',
        launchType='FARGATE',
        taskDefinition='predict_task2',
        count=1,
        overrides={'containerOverrides': [{
            'name': 'deepshack_predict',
            'environment': [{'name': 'IMAGE_ID', 'value': filename},
                            {'name': 'PHONE', 'value': phone_number}]
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
