import boto3
import json


def predict_trigger_handler(event, context):
    # TODO, hardcoding for testing
    # Receive message from scraper service on the triggerPredict SNS topic:
    # inbound_message = json.loads(event['Records'][0]['Sns']['Message'])
    # image_id = inbound_message['image_id']
    # phone = inbound_message['phone']

    image_id = 'shackcam/2019-05-05_1658_2065125031.jpg'
    phone = '785-979-7432'

    ecs = boto3.client('ecs')
    response = ecs.run_task(
        cluster='cluster2',
        launchType='FARGATE',
        taskDefinition='predict_task',
        count=1,
        overrides={'containerOverrides': [{
            'name': 'deepshack_predict_container',
            'environment': [{'name': 'IMAGE_ID', 'value': image_id},
                            {'name': 'PHONE', 'value': phone}]
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
    return response
