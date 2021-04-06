from setuptools import setup

setup(
    name='Shotty',
    version='0.1',
    author='bofus',
    description='Tool to manage EC2 Instances',
    license='GPLv3+',
    packages=['shotty'],
    install_requires=[
        'click',
        'boto3',
        'botocore'
    ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    ''',
)
