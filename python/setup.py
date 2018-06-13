#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

version = '0.0.1'

install_requires = [
    'six',
    'llsmartcard-ph4',
]

dev_extras = [
    'pep8',
    'tox',
    'pandoc',
    'pypandoc',
    'python-afl',
]


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
    long_description = long_description.replace("\r", '')

except(IOError, ImportError):
    import io
    with io.open('README.md', encoding='utf-8') as f:
        long_description = f.read()


setup(
    name='apdu-fuzzer',
    version=version,
    description='APDU fuzzer',
    long_description=long_description,
    url='https://github.com/petrs/APDUFuzzer',
    author='Petr Svenda',
    author_email='svenda@fi.muni.cz',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security',
    ],

    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'dev': dev_extras,
    },
)
