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

import logging

LOG = logging.getLogger(__name__)

def get_logging_configuration(**configuration):
    """Load the configuration for logging. """

   
    steam_handler = logging.StreamHandler()
    steam_handler.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s'))
    LOG.setLevel(logging.INFO)
    LOG.addHandler(steam_handler)

    return LOG


