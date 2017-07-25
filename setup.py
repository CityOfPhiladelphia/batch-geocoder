#!/usr/bin/env python

from distutils.core import setup

setup(
    name='batch_geocoder',
    version='0.1dev',
    packages=['batch_geocoder'],
    install_requires=[
        'boto3==1.4.4',
        'click==6.7',
        'smart_open==1.5.2'
    ],
    entry_points={
        'console_scripts': [
            'batch_geocoder=batch_geocoder:geocode',
        ],
    },
)
