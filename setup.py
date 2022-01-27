#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as changelog_file:
    changelog = changelog_file.read()


requirements = [
    'CherryPy==18.1.1',
    'Click==7.0',
    'PyYAML==5.4',
    'mock==3.0.5',
    'prometheus_client==0.6.0',
    'pyfakefs==3.5.8',
    'pylint==2.3.1',
    'pysnmp==4.4.8',
    'pytest==4.4.0',
    'python-dateutil==2.8.0',
    'pytest-runner==5.3.1',
]

dependency_links = [
]

test_requirements = [
    # TODO: put package test requirements here
]

setuptools.setup(
    name='prometheus-webhook-snmp',
    version='1.5',
    description=("Prometheus Alertmanager receiver for SNMP traps"),
    long_description=readme + '\n---\n' + changelog,
    long_description_content_type='text/markdown',
    url='https://github.com/infrawatch/prometheus-webhook-snmp',
    py_modules=['prometheus_webhook_snmp.prometheus_webhook_snmp', 'prometheus_webhook_snmp.utils'],
    include_package_data=True,
    dependency_links=dependency_links,
    install_requires=requirements,
    license="GPLv3",
    data_files=[
        ('./share/doc/prometheus-webhook-snmp', ['CHANGELOG.md', 'README.md']),
    ],
    zip_safe=True,
    keywords='prometheus_webhook_snmp',
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'prometheus-webhook-snmp=prometheus_webhook_snmp.prometheus_webhook_snmp:cli',
        ],
    }
)
