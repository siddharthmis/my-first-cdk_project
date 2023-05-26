import boto3
import json
import zlib
import os
import logging
from splunk_http_event_collector import http_event_collector

loggerConfig = {
    'url': os.environ['splunk_hec_url'],
    'token': os.environ['splunk_hec_token'],
    'maxBatchCount': 0, # Manually flush events
    'maxRetries': 3,    # Retry 3 times
}

hec = http_event_collector(token=loggerConfig['token'], http_event_server=loggerConfig['url'])

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info('Received event: ' + json.dumps(event, indent=2))
    sourcetype = 'aws:cloudwatchlogs'
    # CloudWatch Logs data is base64 encoded so decode here
    payload = zlib.decompress(base64.b64decode(event['awslogs']['data']), 16+zlib.MAX_WBITS)
    parsed = json.loads(payload)
    if parsed['logGroup'] == 'AWS-CLOUD2-GD-SECURITY':
        sourcetype = 'aws:cloudwatch:guardduty'
    for logEvent in parsed['logEvents']:
        event = {
            'event': logEvent['message'],
            'sourcetype': sourcetype,
            'source': parsed['logStream'],
            'time': logEvent['timestamp'] / 1000
        }
        hec.batchEvent(event)
    hec.flushBatch()

import json
import time
import requests

def handler(event, context):
    payload = event['awslogs']['data']
    decoded = json.loads(json.loads(payload).decode('base64'))
    count = 0
    if 'logEvents' in decoded:
        for item in decoded['logEvents']:
            if item['message'].strip() != "":
                data = {
                    'message': item['message'],
                    'metadata': {
                        'time': int(time.mktime(time.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ'))),
                        'host': 'serverless',
                        'source': decoded['logGroup'],
                        'sourcetype': sourcetype,
                        'index': 'aws_cloudwatch'
                    }
                }
                response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
                response.raise_for_status()
            count += 1
    print('Successfully processed {} log event(s).'.format(count))
    return count
	
def configureLogger(context, callback):
    # Override SplunkLogger default formatter
    logger.eventFormatter = lambda event: (
        # Enrich event only if it is an object
        event.update({'awsRequestId': context.awsRequestId}) or event
        if isinstance(event, dict) and 'awsRequestId' not in event
        else event
    )
    # Set common error handler for logger.send() and logger.flush()
    def error_handler(error, payload):
        print('error', error, 'context', payload)
        callback(error)
    logger.error = error_handler
