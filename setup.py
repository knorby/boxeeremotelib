#!/usr/bin/env python
from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='boxeeremotelib',
    version='0.1',
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    packages=['boxeeremotelib'],
    entry_points = {
        'console_scripts': [
            'boxee_discover = boxeeremotelib.discoverer:main',
            'boxee_command = boxeeremotelib:main'
            ],
        },
    author = "Kali Norby",
    author_email = "kali.norby@gmail.com",
    description = ("an interface to the boxee remote api"),
    license = "BSD",
    keywords = "boxee remote entertainment library",
    url = "https://github.com/knorby/boxeeremotelib",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Topic :: Multimedia :: Sound/Audio :: Players"
        ],
    )
