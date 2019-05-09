import json
import os
import tempfile
import logging

import boto3
import cv2
import numpy as np
from tensorflow.python.keras.models import load_model


S3_BUCKET = 'deepshack'
MODEL_PATH = 'model/vgg16_shackcam.h5'
MASK_PATH = 'train/data/shackcam/line_mask.png'
TOPIC_ARN = 'arn:aws:sns:us-east-1:245636212397:dlresult'


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

    pred = int(round(model.predict(masked_image)[0][0]))
    return pred


def publish_message(message):
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn=TOPIC_ARN,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )

    return response


def run():
    image_id = os.getenv('IMAGE_ID')
    phone = os.getenv('PHONE')

    prediction = predict(image_id)
    message = {'image_id': image_id, 'phone': phone, 'prediction': prediction}
    logging.info(message)

    response = publish_message(message)
    logging.info(response)


if __name__ == '__main__':
    run()
