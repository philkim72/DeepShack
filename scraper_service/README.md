# Scraper Service

## DESCRIPTION
Shake Shack provides real-time images of the store-front on the Shake Shack website. In order to count the number of people in line, we use these images as our starting point.

This scraper service downloads the images and saves them to S3. From S3, the images are used by downstream services. The service can be run on a schedule or triggered by a user-initiated request such as a text message.

* The Scraper Service is subscribed to the *triggerScrape* topic.
* The Scraper Service publishes topics such as *triggerPredict* and *triggerSMS*

## DEPENDENCIES
This service has three dependencies:

1. AWS Lambda
2. Python Libraries
3. Amazon S3

#### 1. AWS Lambda

This is an Amazon product that allows you to create serverless applications. One can create an account and get started with Lambda here: https://aws.amazon.com/lambda/


#### 2. Python Libraries

This service depends on two python libraries:


a. requests

This library allows you to make HTTP requests with Python. It is readily available with AWS Lambda. Simply including the following code in your Lambda function:

`from botocore.vendored import requests`


b. fake_useragent

We use this library in conjunction with the requests library because, when making repeated HTTP requests, we want to simulate using different browsers for each programmatic request.

Because this library is not readily available to AWS Lambda, we have to upload it to AWS. The process is as follows (see here for detailed instructions <https://medium.com/@qtangs/creating-new-aws-lambda-layer-for-python-pandas-library-348b126e9f3e>):

Install package locally by creating a `requirements.txt` file containing the following:

```
fake-useragent==0.1.11
```

Create the following packaging script. When executed, this will install the packages in your requirements file:

```
#!/bin/bash

export PKG_DIR="python"

rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}

docker run --rm -v $(pwd):/foo -w /foo lambci/lambda:build-python3.6 \
    pip install -r requirements.txt --no-deps -t ${PKG_DIR}
```

Execute the packaging script to create zip file:

```
chmod +x get_layer_packages.sh
./get_layer_packages.sh
zip -r my-Python36-Pandas23.zip .
```

Once you have created a zipfile with the fake_useragent library, upload it to your Lambda function with the UI.


#### 3. Amazon S3

We chose Amazon S3 to store scraped images. After setting up an S3 bucket, we needed to grant our scraper service "full access" to the S3 bucket. This enables the service to write to S3. Access to S3 can be granted through Amazon's IAM UI.

## INPUT
The Scraper services subscribes to the AWS SNS topic *triggerScrape* which will contain the variable *phone_number* which contains the user's phone number.

Below is a portion of the JSON received by this service:

```
{ 
    'phone_number': phone_number, 
}
```

## OUTPUT
The Scraper service publishes two separate AWS SNS topics.

* *triggerPredict*: This topic is subscribed by the PredictTrigger Service.  It will contain the two variables *filename* which is the name of the ShackCam image that is saved in S3 and *phone_number* which contains the user's phone number.

```
{
    'phone_number': phone_number,
    'filename': filename
}
```

* *triggerSMS*: This topic is subscribed by the Outbound SMS Service.  It will contain two variables *phone_number* which contains the user's phon number and *body* which contains a status message for transmission back to the user in real-time.

```
{
    'phone_number': phone_number,
    'body': body
}
```

## TEST CASE
* Example of JSON to run a test
* Describe expected behaviour
