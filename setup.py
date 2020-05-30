#!/usr/bin/env python3

from setuptools import setup, find_packages


__version__ = "1.0"

setup(
    name='ndn-python-catalog',
    version=__version__,
    description='An NDN catalog implementation using Python',
    url='https://github.com/satyaprakash-1729/ndn-python-catalog',
    author='Satya Prakash',
    author_email='prakashsatya@cs.ucla.edu',
    download_url='https://pypi.python.org/pypi/ndn-python-catalog',
    project_urls={
        "Bug Tracker": "https://github.com/satyaprakash-1729/ndn-python-catalog/issues",
        "Source Code": "https://github.com/satyaprakash-1729/ndn-python-catalog",
    },
    license='Apache License 2.0',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Topic :: Database',
        'Topic :: Internet',
        'Topic :: System :: Networking',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='NDN',

    packages=find_packages(exclude=['tests']),

    install_requires=[
        "python-ndn >= 0.2b2.post1",
        "PyYAML >= 5.1.2",
    ],
    extras_require={
        'test': [ 'pytest', 'pytest-cov']
    },
    python_requires=">=3.6",

    entry_points={
        'console_scripts': [
            'ndn-python-catalog = ndn_python_catalog.main:main',
            'ndn-python-catalog-install = ndn_python_catalog.install:main',
        ],
    },

    data_files=[
        # ('/usr/local/etc/ndn', ['ndn_python_repo/ndn-python-repo.conf']),
        # ('/etc/systemd/system/', ['ndn_python_repo/ndn-python-repo.service']),
    ],

    package_data={
        '': ['*.conf', '*.service'],
    },
    include_package_data=True,
)
