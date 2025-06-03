#!/usr/bin/env python3

from prometheus_client import start_http_server, Metric, REGISTRY ,Gauge
import time
import os
import re
import boto3
import datetime

#Try get the TAG_PROJECT env variable. If not defined, we will use the Scost
tagProject = os.getenv('TAG_PROJECT','Scost')
tagProject = 'sc:env'
# Try get the PORT env variable. If not defined, cast the default 9150 to int
port = int(os.getenv('PORT', 9150))

def getCosts():
	#Create a boto3 connection with cost explorer
	client = boto3.client('ce')

	#Get the current time
	now = datetime.datetime.utcnow()

	# Set the end of the range to start of the current day 
	end = datetime.datetime(year=now.year, month=now.month, day=now.day)

	# Subtract a day to define the start of the range 
	start = end - datetime.timedelta(days=30)

	# Convert them to strings
	start = start.strftime('%Y-%m-%d')
	end = end.strftime('%Y-%m-%d')

	print("Starting script searching by the follow time range")
	print(start + " - " + end)

	#Call AWS API to get costs
	response = client.get_cost_and_usage(
		TimePeriod={
			'Start': start,
			'End':  end
		},
		Granularity='MONTHLY',
		Metrics=['BlendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            },
        ]
		
	)
	print (response)
	#Create an empty dictionary
	projectValues = {}

	#Run the response and make a dictionary with tag name and tag value
	for project in response["ResultsByTime"][0]["Groups"]:

		#Search for tag
		namestring = project['Keys'][0]
		name = re.search("\$(.*)", namestring).group(1)

		#If name is none, let's defined it as Other
		if name is None or name == "":
			name = "Other"

		#Get the value
		amount = project['Metrics']['BlendedCost']['Amount']
		#Format the amount to 2 decimal points
		amount = "{0:.2f}".format(float(amount))

		#Append the values in the dictionary
		projectValues[name] = float(amount)

	#Return the dictionary with all those values
	return projectValues


#Start class collector
class costExporter(object):

	def collect(self):

		#Expose the metric
		#Create header
		metric = Metric('aws_project_cost','Total amount of costs for project','gauge')
		cost_metric = Gauge('aws_cost', 'AWS Cost by Service', ['service'])
		
		#Run the retuned dictionary and expose the metrics
		for project,cost in getCosts().items():
			metric.add_sample('aws_project_cost',value=cost,labels={'project':project})

		#/Expose the metric
		yield metric

if __name__ == '__main__':

	start_http_server(port)
        
	metrics = costExporter()
	
	REGISTRY.register(metrics)

	while True: time.sleep(1) 
