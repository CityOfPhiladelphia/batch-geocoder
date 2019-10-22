import re
import sys
import csv
import codecs
import logging

import click
from smart_open import smart_open
import boto
import boto3

from . import ais as ais_geocoder
from .cache import GeocodeCache

csv.field_size_limit(sys.maxsize)

logger = logging.getLogger('batch_geocoder')

handler = logging.StreamHandler(stream=sys.stderr)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)-15s] %(levelname)s [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def exception_handler(type, value, tb):
    logger.exception("Uncaught exception: {}".format(str(value)), exc_info=(type, value, tb))

sys.excepthook = exception_handler

s3_regex = r'^s3://([^/]+)/(.+)'

def fopen(file, mode='r'):
    # HACK: get boto working with instance credentials via boto3
    match = re.match(s3_regex, file)
    if match != None:
        client = boto3.client('s3')
        s3_connection = boto.connect_s3(
            aws_access_key_id=client._request_signer._credentials.access_key,
            aws_secret_access_key=client._request_signer._credentials.secret_key,
            security_token=client._request_signer._credentials.token)
        bucket = s3_connection.get_bucket(match.groups()[0])
        if mode == 'w':
            file = bucket.get_key(match.groups()[1], validate=False)
        else:
            file = bucket.get_key(match.groups()[1])
    return smart_open(file, mode=mode)

def get_stream(file, mode):
    if file:
        return fopen(file, mode=mode)
    else:
        if mode == 'w':
            return sys.stdout
        else:
            return sys.stdin

@click.group()
def geocode():
    pass

@geocode.command()
@click.option('--input-file', help='Input CSV file. Local or S3 (s3://..)')
@click.option('--output-file', help='Output CSV file. Local or S3 (s3://..)')
@click.option('--ais-url', help='Base URL for the AIS service')
@click.option('--ais-key', help='AIS Gatekeeper authentication token')
@click.option('--ais-user', help='Any string indicating the user or usage. This is used for usage and security analysis')
@click.option('--use-cache', is_flag=True, default=False, help='Enable S3 geocode cache')
@click.option('--cache-bucket', help='S3 geocode cache bucket')
@click.option('--cache-max-age', default=90, type=int, help='S3 geocode cache max age in days')
@click.option('--query-fields', help='Fields to query AIS with, comma separated. They are concatenated in order.')
@click.option('--ais-fields', help='AIS fields to include in the output, comma separated.')
@click.option('--remove-fields', help='Fields to remove post AIS query, comma separated.')
def ais(input_file, output_file, ais_url, ais_key, ais_user, use_cache, cache_bucket, cache_max_age, query_fields, ais_fields, remove_fields):
    query_fields = query_fields.split(',')
    ais_fields = ais_fields.split(',')
    out_rows = None

    if use_cache:
        cache = GeocodeCache(bucket=cache_bucket)
    else:
        cache = None

    with get_stream(input_file, 'r') as input_stream:
        with get_stream(output_file, 'w') as output_stream:
            if input_file and re.match(s3_regex, input_file) != None:
                rows = csv.DictReader(codecs.iterdecode(input_stream, 'utf-8'))
            else:
                rows = csv.DictReader(input_stream)

            for row in rows:
                query_elements = []
                for query_field in query_fields:
                    query_elements.append(row[query_field])

                result = None

                if cache:
                    key = ','.join(query_elements)
                    result = cache.get(key, max_age=cache_max_age)

                if not cache or not result:
                    result = ais_geocoder.geocode(ais_url, ais_key, ais_user, query_elements)

                if result and 'features' in result and len(result['features']) > 0:
                    if cache:
                        cache.put(key, result)

                    feature = result['features'][0]
                    for ais_field in ais_fields:
                        if ais_field == 'lon' or ais_field == 'longitude':
                            row[ais_field] = feature['geometry']['coordinates'][0] if feature['geometry']['coordinates'] is not None else ''
                        elif ais_field == 'lat' or ais_field == 'latitude':
                            row[ais_field] = feature['geometry']['coordinates'][1]  if feature['geometry']['coordinates'] is not None else ''
                        else:
                            row[ais_field] = feature['properties'][ais_field]
                else:
                    logger.warn('Could not geocode "{}"'.format(query_elements))

                if out_rows == None:
                    headers = rows._fieldnames + ais_fields
                    out_rows = csv.DictWriter(output_stream, headers)
                    out_rows.writeheader()

                out_rows.writerow(row)
