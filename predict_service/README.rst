==================
Prediction Service
==================

The predict service is implemented as an AWS Lambda function. The service makes a prediction based on the last file added to the “shackcam” S3 bucket by the preceding "scraper" service. The predict service publishes the prediction result to another SNS topic called “dlresult”, to which the email and SMS services are subscribed. 


Prerequisites and Deployment
=============================

Current state: AWS Lambda

Future state: Because our deep neural networks are too large to be deployed to AWS lambda, we are actively exploring the following model storage alternatives:

1. AWS Elastic Container Service
2. AWS SageMaker

