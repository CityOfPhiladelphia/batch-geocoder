# Batch Geocoder

Batch Geocoder takes in a CSV file, either from stdin or a specified path (local and S3), geocodes the rows using specified columns using a geocode provider, and outputs a CSV with the geocoded fields.

## Usage

```
$ batch_geocoder
Usage: batch_geocoder [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  ais
```

### AIS Provider

[Address Information System](https://github.com/CityOfPhiladelphia/ais) is a geocoder built for geocoding within the city of Philadelphia.

```
$ batch_geocoder ais --help
Usage: batch_geocoder ais [OPTIONS]

Options:
  --input-file TEXT        Input CSV file. Local or S3 (s3://..)
  --output-file TEXT       Output CSV file. Local or S3 (s3://..)
  --ais-url TEXT           Base URL for the AIS service
  --ais-key TEXT           AIS Gatekeeper authentication token
  --ais-user TEXT          Any string indicating the user or usage. This is
                           used for usage and security analysis
  --use-cache              Enable S3 geocode cache
  --cache-bucket TEXT      S3 geocode cache bucket
  --cache-max-age INTEGER  S3 geocode cache max age in days
  --query-fields TEXT      Fields to query AIS with, comma separated. They are
                           concatenated in order.
  --ais-fields TEXT        AIS fields to include in the output, comma
                           separated.
  --remove-fields TEXT     Fields to remove post AIS query, comma separated.
  --help                   Show this message and exit.
```

Columns available for `--ais-fields` include any field available in the resulting matched geometry's `features`.