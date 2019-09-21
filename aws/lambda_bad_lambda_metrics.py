#!/bin/python3

import boto3
import datetime
import csv

if __name__ == '__main__':

    regions = ['ap-southeast-1', 'us-east-1', 'ap-south-1']
    values = []

    for region in regions:

        # Get list of all Lambdas
        next_token = ''
        client = boto3.client('lambda', region_name=region)

        lambdas = []
        while next_token != None:

            params = {'MaxItems': 50}
            if next_token != '':

                params['Marker'] = next_token

            response = client.list_functions(
                **params
            )

            for item in response['Functions']:

                lambdas.append(item['FunctionName'])

            next_token = response['NextMarker'] if 'NextMarker' in response else None

        # Get metrics for Lambdas
        client = boto3.client('cloudwatch', region_name=region)
        next_token = ''

        for my_lambda in lambdas:

            print('> Processing %s...' % (my_lambda))

            params = {

                'MetricDataQueries': [
                    {
                        'Id': 'errors',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Lambda',
                                'MetricName': 'Errors',
                                'Dimensions': [
                                    {
                                        'Name': 'FunctionName',
                                        'Value': my_lambda
                                    },
                                ]
                            },
                            'Period': 86400,
                            'Stat': 'Sum',
                            'Unit': 'Count'
                        },
                    },                    
                    {
                        'Id': 'invocations',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Lambda',
                                'MetricName': 'Invocations',
                                'Dimensions': [
                                    {
                                        'Name': 'FunctionName',
                                        'Value': my_lambda
                                    },
                                ]
                            },
                            'Period': 86400,
                            'Stat': 'Sum',
                            'Unit': 'Count'
                        },
                    },
                    {
                        'Id': 'duration',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Lambda',
                                'MetricName': 'Duration',
                                'Dimensions': [
                                    {
                                        'Name': 'FunctionName',
                                        'Value': my_lambda
                                    },
                                ]
                            },
                            'Period': 86400,
                            'Stat': 'Average',
                            'Unit': 'Milliseconds'
                        },
                    },
                    {
                        'Id': 'throttles',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Lambda',
                                'MetricName': 'Throttles',
                                'Dimensions': [
                                    {
                                        'Name': 'FunctionName',
                                        'Value': my_lambda
                                    },
                                ]
                            },
                            'Period': 86400,
                            'Stat': 'Sum',
                            'Unit': 'Count'
                        },
                    },
                ],
                'StartTime': datetime.datetime.utcnow() - datetime.timedelta(hours=1),
                'EndTime': datetime.datetime.now(),
                'ScanBy': 'TimestampDescending',
                'MaxDatapoints': 100
            }

            response = client.get_metric_data(

                **params
            )

            if 'MetricDataResults' in response:

                tmp = {'Function': my_lambda, 'region': region}

                for item in response['MetricDataResults']:

                    tmp[item['Label']] = round(
                        item['Values'][0] if 'Values' in item and item['Values'] else 0, 2)

                print('>> Final values: %s' % (str(tmp)))

            values.append(tmp)

    # Write metrics to CSV file
    with open('my_bad_lambdas.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, values[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(values)
