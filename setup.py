#!/usr/bin/env python
from setuptools import setup

setup(
    name='boxeeremotelib',
    version='0.1',
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    packages=['boxeeremotelib'],
    entry_points = {
        'console_scripts': [
            'boxee_discover = boxeeremotelib.discoverer:main',
            'boxee_command = boxeeremotelib:main'
            ],
        },
    )
