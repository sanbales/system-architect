#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='system-architect',
    version="0.0.1",
    install_requires=open('requirements.txt', 'r').read().splitlines(),
    description="A prototype Collaborative System Architecting Tool",
    author='Santiago Balestrini-Robinson',
    author_email='santiago.balestrini@gtri.gatech.edu',
    url='https://bitbucket.org/sanbales/utility-planner',
    packages=find_packages(),
    license='MIT',  # TODO: check with Danny to see what he prefers
    platforms='any',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Manufacturing',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=True,
    long_description=''.join(list(open('README.md', 'r'))[3:]))
