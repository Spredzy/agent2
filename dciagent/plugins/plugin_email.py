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

from dciagent.plugins import plugin

import os
import random
import string
import subprocess


class Email(plugin.Plugin):

    def __init__(self, conf):
        super(Email, self).__init__(conf)

    def run(self, state, data=None, context=None):
        """Send a notification email. """

        subject = self.conf[state]['subject']
        message = self.conf[state]['message']

        smtp_server = self.conf['smtp_server']
        smtp_port = self.conf['smtp_port']
        smtp_user = self.conf['smtp_user']
        smtp_passwd = self.conf['smtp_password']
        smtp_recpt = self.conf['smtp_recpt']

        subj = self.format(subject, data, context)
        msg = self.format(message, data, context)

        ansible_play = """
- hosts: localhost
  tasks:
    - mail: host='%s'
            port=%s
            username='%s'
            password='%s'
            to='%s'
            subject='%s'
            body='%s'

""" % (smtp_server, smtp_port, smtp_user, smtp_passwd, smtp_recpt, subj, msg)

        for _ in range(10):
            tmp_string = random.choice(string.ascii_uppercase + string.digits)
            rand_string = ''.join(tmp_string)

        open('/tmp/%s.yml' % rand_string, 'w').write(ansible_play)
        p = subprocess.Popen(['ansible-playbook', '/tmp/%s.yml' % rand_string],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        os.remove('/tmp/%s.yml' % rand_string)

        return 0
