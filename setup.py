from setuptools import find_packages, setup

setup(
    name='pyntercrate',
    author='stadust',
    description='A minimal pointercrate API wrapper',
    packages=find_packages(),
    version='1.0.5',
    install_requires=['aiohttp==2.0.0']
)
