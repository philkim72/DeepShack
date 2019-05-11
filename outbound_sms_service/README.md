# NAME OF THE FUNCTION

## DESCRIPTION

This microservice sends SMS messages to the end user. It receives messages from all other microservices and updates the user when those microservices have completed.

Input: outbound_sms is subscribed to the triggerSMS topic.
Output: outbound_sms makes an HTTP POST request to Twilio, which sends an SMS to the end user.

## DEPENDENCIES
* base64
* json
* os
* urllib

## ROLE

This AWS role requires the following permissions:
* AWS SNS full access
* AWS lambda basic execution role

## INPUT

This microservice receives the following message structure from all other microservices:

"""
{
    'phone_number': phone_number,
    'body': body
}
"""


## OUTPUT

This microservice passes the following parameters to Twilio via a POST request:

"""
{
    "To": to_number, 
    "From": from_number, 
    "Body": body
}
"""

