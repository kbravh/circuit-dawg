#! /usr/bin/env python
from setuptools import setup

setup(
    name="circuit-dawg",
    version="1.0.0",
    description="Pure-python reader for DAWGs (DAFSAs) that were created by dawgdic C++ library or the DAWG Python library                . Optimized to run on CircuitPython.",
    long_description = open('README.md').read(),
    author='Karey Higuera',
    author_email='karey.higuera@gmail.com',
    url='https://github.com/kbravh/circuit-dawg/',
    packages = ['circuit-dawg'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Linguistic',
    ],
)
