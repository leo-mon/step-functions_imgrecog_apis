from __future__ import print_function
import boto3
import json

print('Loading function')

rekognition = boto3.client('rekognition', region_name='us-west-2')
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


def detect_labels(binary, maxlabels, minconfidence):
    """
    Detect labels on a picture using Rekognition API
    :param binary: binary strings of a image
    :param maxlabels: (int) Maximum numbers of labels
    :param minconfidence: (float) minimum limit of confidence (>50.0)
    :return: JSON strings
    """
    response = rekognition.detect_labels(Image={'Bytes': binary}, MaxLabels=maxlabels, MinConfidence=minconfidence)
    return response

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

    # Call Rekognition API
    try:
        # Calls rekognition DetectLabels API to detect labels in S3 object
        response = detect_labels(binary=img_bin, maxlabels=10, minconfidence=50.0)
        print('Response: ' + json.dumps(response, indent=2))
        return response
    except Exception as e:
        print(e)
        raise e
