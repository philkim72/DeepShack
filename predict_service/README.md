==================
Prediction Service
==================

The predict service is implemented as an AWS Lambda function. The service makes a prediction based on the last file added to the `shackcam` S3 bucket by the preceding "scraper" service. The predict service publishes the prediction result to another SNS topic called `dlresult`, to which the email and SMS services are subscribed.


How to build a Docker image and deploy to ECS
=============================
aws ecr get-login --no-include-email --region us-east-1
    docker login -u AWS -p **** 245636212397.dkr.ecr.us-east-1.amazonaws.com
    docker tag deepshack_predict:latest 245636212397.dkr.ecr.us-east-1.amazonaws.com/deepshack_predict:latest
    docker push 245636212397.dkr.ecr.us-east-1.amazonaws.com/deepshack_predict:latest
