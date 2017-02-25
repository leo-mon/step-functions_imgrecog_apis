from __future__ import print_function
from datetime import datetime
import json
import urllib
import boto3

print('Loading function')

s3 = boto3.client('s3', region_name='ap-northeast-1')
sfn = boto3.client('stepfunctions', region_name='ap-northeast-1')
stateMachineArn = '{STATE_MACHINE_ARN}'


def lambda_handler(event, context):
    """
    :param event: Receive s3putObject event
    :return: JSON Strings of startExecution response
    """
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(
              event['Records'][0]['s3']['object']['key'].encode('utf8')
          )
    try:
        response = sfn.start_execution(
                       stateMachineArn=stateMachineArn,
                       name='FromLambda'+datetime.now().strftime('%Y%m%d%H%M%S'),
                       input=json.dumps({'bucket': bucket, 'key': key})
                    )
        return json.loads(response)
    except Exception as e:
        print(e)
        raise e
