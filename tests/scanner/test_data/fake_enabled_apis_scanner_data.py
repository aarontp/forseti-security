# Copyright 2018 The Forseti Security Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Fake Enabled APIs data."""

from google.cloud.forseti.scanner.audit import enabled_apis_rules_engine


API_COMPUTE = {
    "config": {
        "name": "compute.googleapis.com"},
    "state": "ENABLED"}

API_LOGGING = {
    "config": {
        "name": "logging.googleapis.com"},
    "state": "ENABLED"}

API_MONITORING = {
    "config": {
        "name": "monitoring.googleapis.com"},
    "name": "projects/123/services/monitoring.googleapis.com",
    "state": "ENABLED"}

API_PUBSUB = {
    "config": {
        "name": "pubsub.googleapis.com"},
    "state": "ENABLED"}

API_STORAGE = {
    "config": {
        "name": "storage.googleapis.com"},
    "state": "ENABLED"}

ENABLED_APIS_RESOURCES = [
    {
        'project_name': 'proj-1',
        'project_full_name': 'organization/234/project/proj-1/',
        'enabled_apis': [API_COMPUTE, API_LOGGING, API_MONITORING, API_STORAGE],
    },
    {
        'project_name': 'proj-2',
        'project_full_name': 'organization/234/project/proj-2/',
        'enabled_apis': [API_COMPUTE, API_LOGGING, API_STORAGE],
    },
    {
        'project_name': 'proj-3',
        'project_full_name': 'organization/234/folder/333/project/proj-3/',
        'enabled_apis': [API_LOGGING, API_MONITORING, API_PUBSUB, API_STORAGE],
    },
]

RuleViolation = enabled_apis_rules_engine.Rule.RuleViolation

ENABLED_APIS_VIOLATIONS = [
    # Rule 0 whitelists COMPUTE, LOGGING, MONITORING.
    RuleViolation(resource_type='project',
                  resource_id='proj-1',
                  full_name='organization/234/project/proj-1/',
                  rule_name='Test whitelist',
                  rule_index=0,
                  violation_type='ENABLED_APIS_VIOLATION',
                  apis=[API_STORAGE.get('config', {}).get('name')],
                  resource_data='project-1-data',
                  resource_name='proj-1'),
    RuleViolation(resource_type='project',
                  resource_id='proj-2',
                  full_name='organization/234/project/proj-2/',
                  rule_name='Test whitelist',
                  rule_index=0,
                  violation_type='ENABLED_APIS_VIOLATION',
                  apis=[API_STORAGE.get('config', {}).get('name')],
                  resource_data='project-2-data',
                  resource_name='proj-2'),
    RuleViolation(resource_type='project',
                  resource_id='proj-3',
                  full_name='organization/234/folder/333/project/proj-3/',
                  rule_name='Test whitelist',
                  rule_index=0,
                  violation_type='ENABLED_APIS_VIOLATION',
                  apis=[API_PUBSUB.get('config', {}).get('name'),
                        API_STORAGE.get('config', {}).get('name')],
                  resource_data='project-3-data',
                  resource_name='proj-3'),
    # Rule 1 blacklists PUBSUB.
    RuleViolation(resource_type='project',
                  resource_id='proj-3',
                  full_name='organization/234/folder/333/project/proj-3/',
                  rule_name='Test blacklist',
                  rule_index=1,
                  violation_type='ENABLED_APIS_VIOLATION',
                  apis=[API_PUBSUB.get('config', {}).get('name')],
                  resource_data='project-3-data',
                  resource_name='proj-3'),
    # Rule 2 requires LOGGING and MONITORING.
    RuleViolation(resource_type='project',
                  resource_id='proj-2',
                  full_name='organization/234/project/proj-2/',
                  rule_name='Test required list',
                  rule_index=2,
                  violation_type='ENABLED_APIS_VIOLATION',
                  apis=[API_MONITORING.get('config', {}).get('name')],
                  resource_data='project-2-data',
                  resource_name='proj-2'),
]

FLATTENED_ENABLED_APIS_VIOLATIONS = [
    {
        'resource_type': 'project',
        'resource_id': 'proj-1',
        'resource_name': 'proj-1',
        'full_name': 'organization/234/project/proj-1/',
        'rule_name': 'Test whitelist',
        'rule_index': 0,
        'violation_type': 'ENABLED_APIS_VIOLATION',
        'violation_data': {
            'api_name': 'storage.googleapis.com',
            'full_name': 'organization/234/project/proj-1/'
        },
        'resource_data': 'project-1-data'
    },
    {
        'resource_type': 'project',
        'resource_id': 'proj-2',
        'resource_name': 'proj-2',
        'full_name': 'organization/234/project/proj-2/',
        'rule_name': 'Test whitelist',
        'rule_index': 0,
        'violation_type': 'ENABLED_APIS_VIOLATION',
        'violation_data': {
            'api_name': 'storage.googleapis.com',
            'full_name': 'organization/234/project/proj-2/'
        },
        'resource_data': 'project-2-data'
    },
    {
        'resource_type': 'project',
        'resource_id': 'proj-3',
        'resource_name': 'proj-3',
        'full_name': 'organization/234/folder/333/project/proj-3/',
        'rule_name': 'Test whitelist',
        'rule_index': 0,
        'violation_type': 'ENABLED_APIS_VIOLATION',
        'violation_data': {
            'api_name': 'pubsub.googleapis.com',
            'full_name': 'organization/234/folder/333/project/proj-3/'
        },
        'resource_data': 'project-3-data'
    },
    {
        'resource_type': 'project',
        'resource_id': 'proj-3',
        'resource_name': 'proj-3',
        'full_name': 'organization/234/folder/333/project/proj-3/',
        'rule_name': 'Test whitelist',
        'rule_index': 0,
        'violation_type': 'ENABLED_APIS_VIOLATION',
        'violation_data': {
            'api_name': 'storage.googleapis.com',
            'full_name': 'organization/234/folder/333/project/proj-3/'
        },
        'resource_data': 'project-3-data'
    },
    {
        'resource_type': 'project',
        'resource_id': 'proj-3',
        'resource_name': 'proj-3',
        'full_name': 'organization/234/folder/333/project/proj-3/',
        'rule_name': 'Test blacklist',
        'rule_index': 1,
        'violation_type': 'ENABLED_APIS_VIOLATION',
        'violation_data': {
            'api_name': 'pubsub.googleapis.com',
            'full_name': 'organization/234/folder/333/project/proj-3/'
        },
        'resource_data': 'project-3-data'
    },
    {
        'resource_type': 'project',
        'resource_id': 'proj-2',
        'resource_name': 'proj-2',
        'full_name': 'organization/234/project/proj-2/',
        'rule_name': 'Test required list',
        'rule_index': 2,
        'violation_type': 'ENABLED_APIS_VIOLATION',
        'violation_data': {
            'api_name': 'monitoring.googleapis.com',
            'full_name': 'organization/234/project/proj-2/'
        },
        'resource_data': 'project-2-data'
    },
]
