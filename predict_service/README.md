# Prediction Service

## DESCRIPTION

The predict service is implemented using AWS ECS. The service will read h5 (model and weights file for trained neural network) to create neural network and make prediction on input image.

## DEPENDENCIES

* Machine Learning Library: TensorFlow, Keras
* Other Python libraries: pandas, matplotlib, PIL, cv2

## INPUT

The service will read image name from ECS environment variable.

## OUTPUT

The predict service publishes the prediction result to SNS topic called `tirggerSMS`, to which Outbound SMS service is subscribed.

## Deployment to ECS

```
docker build --no-cache --tag=deepshack_predict .
aws ecr get-login --no-include-email --region us-east-1
docker login -u AWS -p **** 245636212397.dkr.ecr.us-east-1.amazonaws.com
docker tag deepshack_predict:latest 245636212397.dkr.ecr.us-east-1.amazonaws.com/deepshack_predict:latest
docker push 245636212397.dkr.ecr.us-east-1.amazonaws.com/deepshack_predict:latest
```
