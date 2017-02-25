from __future__ import print_function
import boto3
import json
import decimal

print('Loading function')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('{TABLENNAME}')


def lambda_handler(event, context):
    """
    Rearrange the results and put onto DynamoDB
    :param event: List Object[{amazon: ... },{google: ...},{microsoft }]
    :return: None
    """
    print("Received event: " + json.dumps(event, indent=2))

    results = event
    results_dict = {}
    for result in results:
        results_dict.update(result) # rearrange the result
    item = json.loads(json.dumps(results_dict), parse_float=decimal.Decimal)
    try:
        response = table.put_item(Item=item) # Write on Dynamodb
        print(response)
    except Exception as e:
        print(e)
        raise e
