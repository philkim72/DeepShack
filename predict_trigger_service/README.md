# predict_trigger

## DESCRIPTION
This function reads messages published on the **triggerPredict** SNS topic and passes the <u><i>image_id</i></u> and <u><i>phone</i></u> number to the task **predict_task** contained in the ECS cluster named **cluster2**

## DEPENDENCIES
* Python 3.6
* boto3
* json

## EXECUTION ROLE
The permissions for this function are contained in the role **DeepLambdaRole** with the following policies:
* AmazonS3FullAccess
* AmazonECS_FullAccess
* AmazonSNSFullAccess

## INPUT
It reads the following variables from the message:
* <u>image_id:</u> the id of the variable to use to predict
* <u>phone:</u> phone number to send the SMS message(s)

## OUTPUT
Returns the encoded json response from the call to ECS.

## TEST CASE
* For an example of how to set up a test event see the **test.json** file
