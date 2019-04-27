import json
import random
import tempfile

import numpy as np
import boto3
import cv2
from tensorflow.python.keras.models import load_model


S3_BUCKET = 'deepshack'
MSCNN_MODEL_PATH = 'model/shackcam_final.h5'
FC_MODEL_PATH = 'model/shackcam_fc_final.h5'
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


def transform_image(img, new_shape):
    """Crop, resize, mean normalize, and change from 3D to 4D"""
    img = img[0:720, 0:720]
    img = cv2.resize(img, (new_shape, new_shape)) / 255
    img = np.expand_dims(img, axis=0)  # 3D to 4D
    return img


def mask_image(img):
    img = img[0, :, :, 0].copy()  # 4D to 2D
    new_shape = img.shape[0:2]

    mask = load_s3_object(MASK_PATH, cv2.imread, flags=0)
    mask = cv2.resize(mask, new_shape) // 255
    mask = (mask == 0)
    img[mask] = 0

    img = np.expand_dims(img, axis=0)  # (40, 40) to (1, 40, 40)
    img = np.expand_dims(img, axis=-1)  # (1, 40, 40) to (1, 40, 40, 1)

    return img


def predict(filename):
    img = load_s3_object(filename, cv2.imread)
    gaussian = predict_mscnn(img)
    masked = mask_image(gaussian)
    count = predict_fc(masked)
    return int(round(count))


def predict_mscnn(img):
    model = load_s3_object(MSCNN_MODEL_PATH, load_model)
    new_shape = model.input_shape[1]

    img_4d = transform_image(img, new_shape)
    pred_4d = model.predict(img_4d)
    return pred_4d


def predict_fc(img):
    model = load_s3_object(FC_MODEL_PATH, load_model)
    pred = model.predict(img)
    return pred[0][0]
