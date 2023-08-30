from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name='ideogram_wrapper',
    version='0.0.2',
    description='Generates images from Ideogram API using textual prompts.',
    author='Flowese',
    packages=find_packages(),
    install_requires=requirements,
)
