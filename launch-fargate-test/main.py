import json
import boto3

def lambda_handler(event, context):
    client = boto3.client('ecs')
    response = client.run_task(
    cluster='cluster2', # name of the cluster
    launchType = 'FARGATE',
    taskDefinition='deepshack_predict_task', # replace with your task definition name and revision
    count = 1,
    platformVersion='LATEST',
    networkConfiguration={
        'awsvpcConfiguration': {
            'subnets': [
                'subnet-024f6febf0181b1df', # replace with your public subnet or a private with NAT
                'subnet-0a598f96c9bfcda3a' # Second is optional, but good idea to have two
            ],
            'assignPublicIp': 'ENABLED'
        }
    }
    )
    return str(response)
