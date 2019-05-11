# Inbound SMS Service

## DESCRIPTION

When an end user texts the DeepShack hotline, Twilio makes a POST request to AWS. This service handles that POST request. Specifically, it extracts the user's phone number, which it passess to downstream microservices.

This service publishes messages to the following microservices:
* scraper_service (via the triggerScraper topic)
* outbound_sms_service (via the triggerSMS topic)

## DEPENDENCIES
* boto3
* json

## ROLE

This AWS role requires the following permissions:
* AWS SNS full access
* AWS lambda basic execution role

## INPUT

When Twilio makes a POST request to AWS, the HTTP parameters are split into JSON key value pairs. Below is a portion of the JSON received by this service:

```
{
    'Body': 'Hello+Deep+Shack',
    'To': '<twilio_phone_number>', 
    'From': '<personal_phone_number>', 
}
```

## OUTPUT

This microservice publishes the following two messages:
To scraper service:

```
{
    'phone_number': phone_number
}
```

To outbound_sms service:

```
{
    'phone_number': phone_number,
    'body': body
}
```
