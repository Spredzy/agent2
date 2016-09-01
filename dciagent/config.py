#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import yaml

def load_config(config_path=None):
    """Serialize the configuration file into an object and return it. """

    if config_path:
        file_path = config_path
    elif os.getenv('DCI_AGENT_CONFIG'):
        file_path = os.getenv('DCI_AGENT_CONFIG')
    else:
        file_path = '/etc/dci_agent.conf'
 
    try:
        config = yaml.load(open(file_path, 'r'))
    except OSError, IOError:
        raise
    except yaml.scanner.ScannerError as e:
        raise(e)

    return config
