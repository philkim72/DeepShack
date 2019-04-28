============
sms_service
============
This function will read the messages sent from the predict_service and send a
SMS message to the number stored in the environment variable `ivan_number`.

***************
Dependencies
***************
This function depends on the following packages:

- json
- os
- boto3

***************
Execution
***************
AWS services provides the functionality to trigger notifications to different services like email or SMS via its Simple Notification Services (AWS SNS) by creating a topic (a group of services) and publishing to it. AWS SNS will send the message published to each of the services subscribed to that specific topic. The predict_service publishes to the topic where this function is subscribed.

Upon execution, this function follows these steps:

1. Creates a boto3 session for a specific (geographical) region

2. With that section, it then creates a client for SNS

3. Finally, it uses the client to publish the SMS message

Example
^^^^^^^^^^^^^^^^^^

- predict_service will publish a message similar to this:

.. code-block:: JSON

  {
    "Records": [
    {
      "EventSource": "aws:sns",
      "EventVersion": "1.0",
      "EventSubscriptionArn": "arn:aws:sns:us-east-1:245636212397:dlresult:b2a4ea7f-a427-41c3-8283-f27707aa0929",
      "Sns": {
        "Type": "Notification",
        "MessageId": "3851a2b7-c171-5918-963a-f78a135502a0",
        "TopicArn": "arn:aws:sns:us-east-1:245636212397:dlresult",
        "Subject": "None",
        "Message": {
          "prediction": 6,
          "filename": "2019-04-25_2323-04.jpg"
        },
        "Timestamp": "2019-04-27T03:43:32.490Z",
        "SignatureVersion": "1",
        "Signature": "DxzOXWDeW7TaGPMmrnXjCDxzfUBB9q/su6FOY7BENXbzGFhnm1OthglqDxe1+oGlinD5mM87IoCBzNPN3Vu1lTNXJVoqTvBEwY8F0VwZknPZVXJT/uzsvE45YhR96GbNZimUBYMH7RGDKPh++5ONiPz2UOyzVukOJ2GiIMLIS+oe+i4h+4CiXjhSVXArJDeETkzfAd67s012qObR5ly37BQxyUXWkNaoA/umQorqwDVpvfftFsj7SVSuCbAhYzN4WhrIq63NwYzESi3YwfZ83PXw/abonzy1/9POAm+QMW3ttHyjk6bzcTCRYfe4Nu2uihYF9xYMvTc2ncT0LsMKsA==",
        "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-6aad65c2f9911b05cd53efda11f913f9.pem",
        "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:245636212397:dlresult:b2a4ea7f-a427-41c3-8283-f27707aa0929",
        "MessageAttributes": {}
      }
    }
  ]
  }

- sms_service will read **predict** and **filename** from there
- It will send a SMS to the number stored in the environment variable **ivan_number** saying
    "There are only 6 people in the line"

Improvements for future sprints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Create logic to filter when messages sent to SMS
- Send SMS to a list of subscribers as opposed to a single number
