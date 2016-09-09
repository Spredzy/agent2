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
from dciagent.plugins import irc as plugin_irc
from dciagent.plugins import email as plugin_email
from dciagent.plugins import ansibleplugin as plugin_ansible

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

    GLOBAL_STATUS = 0

    # Parse and retrieve configuration file
    configuration = config.load_config(config_file)

    # Parse and retrieve dci_context
    context = get_dci_context(**configuration['auth'])

    # Retrieve available job
    datas = get_dci_job_data(context, **configuration['dci'])

    states = ['new', 'pre-run', 'running', 'post-run', 'success']
    for state in states:

        if GLOBAL_STATUS != 0:
            break

        if state in configuration['dci']:
            for hook in configuration['dci'][state]:

                if GLOBAL_STATUS != 0:
                    break

                dci_jobstate.create(context, state, 'Running %s hook' % hook, context.last_job_id)

                if hook == 'file':
                    GLOBAL_STATUS = plugin_file.File(configuration[hook]).run(state, data=datas, context=context)
                if hook == 'irc':
                    GLOBAL_STATUS = plugin_irc.Irc(configuration[hook]).run(state, data=datas, context=context)
                if hook == 'ansible':
                    GLOBAL_STATUS = plugin_ansible.AnsiblePlugin(configuration[hook]).run(state, data=datas, context=context)
                if hook == 'email':
                    GLOBAL_STATUS = plugin_email.Email(configuration[hook]).run(state, data=datas, context=context)

    # Handle the push of the last 'success' job state if no plugin
    # have been configured to take an action on success
    if GLOBAL_STATUS == 0 and 'success' not in configuration['dci']:
        dci_jobstate.create(context, 'success', 'Successfully ran the agent', context.last_job_id)


    # Deal with failure state, run on failure actions
    if GLOBAL_STATUS != 0 and 'failure' in configuration['dci']:
        for hook in configuration['dci']['failure']:
            dci_jobstate.create(context, 'failure', 'Running %s hook' % hook, context.last_job_id)

            if hook == 'file':
                plugin_file.File(configuration[hook]).run('failure', data=datas, context=context)
            if hook == 'irc':
                plugin_irc.Irc(configuration[hook]).run('failure', data=datas, context=context)
            if hook == 'ansible':
                plugin_ansible.AnsiblePlugin(configuration[hook]).run('failure', data=datas, context=context)
            if hook == 'email':
                plugin_email.Email(configuration[hook]).run('failure', data=datas, context=context)

    if GLOBAL_STATUS != 0:
        dci_jobstate.create(context, 'failure', 'A failure occured during the agent run', context.last_job_id)
