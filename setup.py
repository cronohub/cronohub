"""Packaging settings."""


from setuptools import Command, find_packages, setup
from cronohub import __version__


with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='cronohub',
    version=__version__,
    include_package_data=True,
    description='Archive your github repositories to anywhere you want.',
    long_description=long_description,
    url='https://github.com/cronohub',
    author='Gergely Brautigam',
    author_email='gergely.brautigam@gmail.com',
    license='LICENSE.txt',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cli,git',
    packages=find_packages(exclude=['docs', 'test*']),
    install_requires=['PyGithub', 'setuptools', 'wheel'],
    entry_points={
        'console_scripts': [
            'cronohub=cronohub.cronohub:main',
        ],
    }
)