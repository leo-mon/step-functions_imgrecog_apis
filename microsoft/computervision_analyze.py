from __future__ import print_function
import httplib
import urllib
import os
import json
import boto3

KEY = os.environ['MS_KEY']

headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': KEY,
}

params = urllib.urlencode({
    # Request parameters
    'visualFeatures': 'Tags',
    'details': 'Celebrities',
    'language': 'en',
})
print('Loading function')

s3 = boto3.resource('s3')

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


def analyze_image(binary):
    body = binary
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/vision/v1.0/analyze?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


# --------------- Main Handler ------------------


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
        # Call Microsoft Computer Vison Analyze API to tag on S3 object
        response = analyze_image(binary=img_bin)
        print('Response: ' + json.dumps(json.loads(response), indent=2))
        return json.loads(response)
    except Exception as e:
        print(e)
        raise e
