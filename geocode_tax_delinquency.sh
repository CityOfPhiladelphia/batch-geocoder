#!/bin/env bash

# https://github.com/CityOfPhiladelphia/property-tax-delinquency-pipeline
# First run the cleanup command
cat $RAW_CSV_FILE  | python tax_delinquency.py cleanup > tax_delinquency_clean.csv
# Use AIS batch-geocoder cli to geocode (https://github.com/CityOfPhiladelphia/batch-geocoder)
cat tax_delinquency_clean.csv | batch_geocoder ais --ais-url http://api.phila.gov/ais/v1/ --query-fields opa_number --ais-fields lat,lon,street_address,zip_code,zip_4,unit_type,unit_num > tax_delinquency_geocoded.csv --ais-key $AIS_KEY
# attempt to fill in the misses (rows AIS could not geocode) using the original address and lat/longs:
cat tax_delinquency_geocoded.csv | python tax_delinquency.py merge_geocodes > tax_delinquency.csv
