import os
import json
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError
from cachetools import LRUCache

class GeocodeCache(object):
    def __init__(self, bucket=None):
        self.client = boto3.client('s3')
        self.bucket = bucket or os.getenv('GEOCODE_CACHE_BUCKET')
        self.memory_cache = LRUCache(maxsize=500)

    def get(self, key, max_age=90):
        try:
            return self.memory_cache[key]
        except:
            pass

        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=key,
                IfModifiedSince=datetime.utcnow() - timedelta(days=max_age))
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchKey':
                raise e
            else:
                return None

        if response['ContentLength'] > 0:
            body = json.loads(response['Body'].read().decode('utf-8'))
            self.memory_cache[key] = body
            return body

        return None

    def put(self, key, body):
        self.memory_cache[key] = body

        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(body).encode('utf-8'))
