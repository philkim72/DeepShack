import json
import random
import tempfile

import numpy as np
import boto3
import cv2
from tensorflow.python.keras.models import load_model


S3_BUCKET = 'deepshack'
MODEL_PATH = 'model/vgg16_shackcam.h5'
MASK_PATH = 'train/data/shackcam/line_mask.png'


def predict_handler(event, context):
    s3_message = event['Records'][0]['s3']

    message = {'prediction': random.randint(0, 10),
               'filename': s3_message['object']['key']}

    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:245636212397:dlresult',
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )

    return {'statusCode': 200, 'body': json.dumps(message)}


def load_s3_object(key, func, **kwargs):
    # Load S3 object as byte string
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    bytestr = obj['Body'].read()

    # Create a temp file and read it with the supplied function
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(bytestr)
        data = func(tmp.name, **kwargs)

    return data


def load_masked_image(filename, new_shape):
    # Load image
    img = load_s3_object(filename, cv2.imread)
    img = cv2.resize(img, new_shape) / 255

    # Load mask
    mask = load_s3_object(MASK_PATH, cv2.imread, flags=0)
    mask = cv2.resize(mask, new_shape) // 255
    mask = (mask == 0)

    # Apply mask
    img[mask] = 0

    # Change shape from (120, 120, 3) to (1, 120, 120, 3)
    img = np.expand_dims(img, axis=0)
    return img


def predict(filename):
    model = load_s3_object(MODEL_PATH, load_model)
    new_shape = model.input_shape[1:3]  # (120, 120) for example
    masked_image = load_masked_image(filename, new_shape)

    pred = model.predict(masked_image)
    return pred[0][0]
