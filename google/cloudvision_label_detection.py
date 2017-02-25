from __future__ import print_function
import os
import json
import base64
import urllib2
import boto3

print('Loading function')

GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate'
KEY = os.environ['GGL_KEY']

s3 = boto3.resource('s3', region_name='ap-northeast-1')

# --------------- Helper Functions to call Rekognition APIs ------------------


def get_object_body(bucket, key):
    """
    Get object body in S3
    :param bucket: bucket name
    :param key: object key
    :return: binary strings
    """
    obj = s3.Object(bucket, key)
    response = obj.get()
    body = response['Body'].read()
    return body


def detect_labels(binary, maxresults):
    """
    Detect labels on a image binary using Google Cloud Vision API
    :param binary: binary of a image
    :return: JSON Strings of detection
    """
    encoded_img = base64.b64encode(binary).decode('utf-8')  # encode image binary into base64
    # Request parameters
    url = '{}?key={}'.format(GOOGLE_CLOUD_VISION_API_URL, KEY)
    data = json.dumps({
        'requests': [{
            'image': {
                'content': encoded_img
            },
            'features': [{
                'type': 'LABEL_DETECTION',
                'maxResults': maxresults
            }]
        }]
    })
    print(url)
    print(data)

    # Requesting
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_data(data)
    res = urllib2.urlopen(req)
    result = res.read()
    return result

# --------------- Main handler ------------------


def lambda_handler(event, context):
    """
    :param event: {bucket: bucket name passed by step functions, key: object name}
    :return: JSON Strings of detection result
    """
    print('Received event: ' + json.dumps(event, indent=2))

    # Get the bucket name and the key from the event
    bucket = event['bucket']
    key = event['key']
    print('Bucket is: ' + bucket)
    print('Key is: ' + key)

    # Get the image binary
    img_bin = get_object_body(bucket=bucket, key=key)

    try:
        # Call Google Cloud Vision DetectLabels API to detect labels in S3 object
        response = detect_labels(binary=img_bin, maxresults=10)
        print('Response: ' + json.dumps(json.loads(response), indent=2))
        return json.loads(response)
    except Exception as e:
        print(e)
        raise e
