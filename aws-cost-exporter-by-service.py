from prometheus_client import start_http_server, Gauge
import boto3
import time
import datetime

def get_cost_by_service(start_date, end_date):
    client = boto3.client('ce', region_name='us-east-1')  # Replace 'us-east-1' with your desired AWS region
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='DAILY',
        Metrics=['BlendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            },
        ]
    )

    return response['ResultsByTime']

#start_date = '2023-07-01'
#end_date = '2023-07-07'

#Get the current time
now = datetime.datetime.utcnow()

# Set the end of the range to start of the current day 
end_date = datetime.datetime(year=now.year, month=now.month, day=now.day)

# Subtract a day to define the start of the range 
start_date = end_date - datetime.timedelta(days=1)

# Convert them to strings
start_date = start_date.strftime('%Y-%m-%d')
end_date = end_date.strftime('%Y-%m-%d')

print("Starting script searching by the follow time range")
print(start_date + " - " + end_date)

# Create Prometheus Gauge metric
cost_metric = Gauge('aws_cost', 'AWS Cost by Service', ['service'])

# Start Prometheus HTTP server
start_http_server(9150)

while True:
    cost_data = get_cost_by_service(start_date, end_date)
    print (cost_data)
    # Reset metric values
    cost_metric._metrics.clear()
    
    for result in cost_data:
        for group in result['Groups']:
            service = group['Keys'][0]
            cost = group['Metrics']['BlendedCost']['Amount']
            
            # Set metric value
            cost_metric.labels(service=service).set(float(cost))
    
    # Sleep for an interval (e.g., 1/2 hour)
    time.sleep(1800)
