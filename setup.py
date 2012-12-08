#!/usr/bin/env python
from setuptools import setup

setup(
    name='boxeeremoteproxy',
    version='0.1',
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    packages=['boxeeproxy'],
    entry_points = {
        'console_scripts': [
            'boxee_discover = boxeeproxy.discoverer:main'
            ],
        },
    )
