#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='system-architect',
    version="0.0.1",
    install_requires=open('requirements.txt', 'r').read().splitlines(),
    description="A prototype Collaborative System Architecting Tool",
    author='Santiago Balestrini-Robinson',
    author_email='sanbales@gmail.com',
    url='https://github.com/sanbales/system-architect',
    packages=find_packages(),
    license='GPLv3',
    platforms='any',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Manufacturing',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
    ],
    include_package_data=True,
    zip_safe=True,
    long_description=''.join(list(open('README.md', 'r'))[3:]))
