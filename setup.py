#!/usr/bin/env python

import os
import sys
from setuptools import setup

os.system('make rst')
try:
    readme = open('README.rst').read()
except FileNotFoundError:
    # fallback when installing from source package
    readme = ''

setup(
    name='microscopestitching',
    version=open(os.path.join('microscopestitching', 'VERSION')).read().strip(),
    description='Automatic merge/stitching of regular spaced images',
    long_description=readme,
    author='Arve Seljebu',
    author_email='arve.seljebu@gmail.com',
    url='https://github.com/arve0/microscopestitching',
    packages=[
        'microscopestitching',
    ],
    package_dir={'microscopestitching': 'microscopestitching'},
    package_data={'microscopestitching': ['VERSION']},
    include_package_data=True,
    install_requires=[
        'imreg_dft',
        'scikit-image',
        'numpy',
        'joblib'
    ],
    license='MIT',
    zip_safe=False,
    keywords='microscopestitching',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
