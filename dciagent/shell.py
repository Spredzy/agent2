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

import click

from dciagent import config
from dciagent.plugins import file as plugin_file
from dciagent.plugins import ansible as plugin_ansible

from dciclient.v1.api import job as dci_job
from dciclient.v1.api import jobstate as dci_jobstate
from dciclient.v1.api import context as dci_context
from dciclient.v1.api import remoteci as dci_remoteci
from dciclient.v1.api import topic as dci_topic


def get_dci_context(**auth):
    """Retrieve a DCI context from the dciclient. """

    if 'dci_cs_url' not in auth:
        auth['dci_cs_url'] = 'https://api.distributed-ci.io'

    return dci_context.build_dci_context(**auth)


def get_dci_job_data(ctx, **dci):
    """Retrieve informations about the job to run. """

    topic_id = dci_topic.get(ctx, dci['topic']).json()['topic']['id']
    remoteci_id = dci_remoteci.get(ctx, dci['remoteci']).json()['remoteci']['id']

    r = dci_job.schedule(ctx, remoteci_id, topic_id=topic_id)
    if r.status_code == 412:
        exit(0)
    elif r.status_code != 201:
        exit(1)

    job_full_data = dci_job.get_full_data(ctx, ctx.last_job_id)

    return job_full_data


@click.command()
@click.option('--config-file', envvar='DCI_AGENT_CONFIG', required=False,
              help="DCI CS url.")
def main(config_file=None):
    # Parse and retrieve configuration file
    configuration = config.load_config(config_file)

    # Parse and retrieve dci_context
    context = get_dci_context(**configuration['auth'])

    # Retrieve available job
    datas = get_dci_job_data(context, **configuration['dci'])

    # Run the pre hooks
    # TODO(spredzy); This has to be dynamic
    for hook in configuration['dci']['pre-run']:
        dci_jobstate.create(context, 'pre-run', 'Running %s hook' % hook, context.last_job_id)
        if hook == 'file':
            plugin_file.File(configuration[hook]).run('pre')
        if hook == 'ansible':
            plugin_ansible.Ansible(configuration[hook]).run('pre', data=datas, context=context)

    # Run the command
    dci_jobstate.create(context, 'running', 'Running main command', context.last_job_id)
    for hook in configuration['dci']['run']:
        if hook == 'file':
            plugin_file.File(configuration[hook]).run('run')
        if hook == 'ansible':
            plugin_ansible.Ansible(configuration[hook]).run('run', data=datas, context=context)

    # Retrieve test to run and run them

    # Run the post hooks
    dci_jobstate.create(context, 'success', 'Successfully ran the agent', context.last_job_id)
    print 'Ok!'
