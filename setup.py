from setuptools import setup, find_packages
import os

with open('README.md') as f:
    long_description = f.read()

setup(
    name='dice_vtk',
    version='18.01.0',
    author='DICEhub',
    author_email='info@dicehub.com',
    description='DICE application tools',
    long_description=long_description,
    url='http://dicehub.com',
    packages = find_packages(),
    install_requires=[
        'dice_tools',
        'vtk',
        'numpy'
        ],
)
