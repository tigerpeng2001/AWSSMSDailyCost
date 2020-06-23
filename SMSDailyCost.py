import json
import boto3
import datetime
import string
import random


# AWS SDK Clients
CLOUDWATCH = boto3.client('cloudwatch')


def get_sms_cost(starttime, endtime):
    """Get CloudWatch Metric"""
    id = random.choice(string.ascii_lowercase) + random.choice(string.ascii_uppercase)
    cw_response = CLOUDWATCH.get_metric_data(
        MetricDataQueries=[
            {
                'Id': id,
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/SNS',
                        'MetricName': 'SMSMonthToDateSpentUSD'
                    },
                    'Period': 300,
                    'Stat': 'Maximum'
                },
                'Label': 'SMSMonthToDateSpentUSD',
                'ReturnData': True,
            },
        ],
        EndTime=endtime,
        StartTime=starttime
    )

    return cw_response["MetricDataResults"][0]["Values"][0]

def put_sms_d2M_cost(d2M_cost, currenminute):
    print(d2M_cost)
    response = CLOUDWATCH.put_metric_data(
        Namespace = "CostWatch",
        MetricData = [
            {
                'MetricName': 'SMSDayToMinuteSpentUSD',
                'Unit': 'None',
                'Value': d2M_cost,
                'Timestamp': currenminute
            }])

def lambda_handler(event, context):
    
    today = datetime.date.today()
    fiveminute = datetime.timedelta(minutes=5)
    today0000 = datetime.datetime(today.year, today.month, today.day)
    yesterady2355 = today0000 - fiveminute
    starting_m2d_cost = get_sms_cost(yesterady2355, today0000 )
    # print(starting_m2d_cost)
    curren = datetime.datetime.now()
    currenminute = datetime.datetime(curren.year, curren.month, curren.day, curren.hour, curren.minute)
    currenminute_5 = currenminute - fiveminute
    current_m2d_cost = get_sms_cost(currenminute_5, currenminute)
    # print(current_m2d_cost)
    current_d2M_cost = current_m2d_cost - starting_m2d_cost
    # print(current_d2M_cost)
    put_sms_d2M_cost(current_d2M_cost, currenminute)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Check CloudWatch logs.')
    }
