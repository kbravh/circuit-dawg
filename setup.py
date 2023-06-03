#! /usr/bin/env python
from setuptools import setup

setup(
    name="circuit-dawg",
    version="1.1.0",
    description="Pure-python reader for DAWGs (DAFSAs) that were created by dawgdic C++ library or the DAWG Python library. Optimized to run on CircuitPython.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Karey Higuera',
    author_email='karey.higuera@gmail.com',
    url='https://github.com/kbravh/circuit-dawg/',
    packages=['circuit_dawg'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: MicroPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Linguistic',
    ],
    keywords=[
      'CircuitPython',
      'DAWG',
      'DAFSA',
      'word list'
    ]
)
