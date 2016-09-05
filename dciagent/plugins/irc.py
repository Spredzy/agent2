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

import sys
import socket
import string


class Irc(plugin.Plugin):

    def __init__(self, conf):
        super(Irc, self).__init__(conf)


    def run(self, state, data=None, context=None):
        """Connect to the specified IRC server/channel and post a message. """
        

        readbuffer=""
        message = self.conf[state]['message']

        server = self.conf['server']
        port = self.conf['port']
        chan = self.conf['chan']

        nick = self.conf['nick']
        ident = self.conf['ident']
        realname = self.conf['realname']

        s=socket.socket( )
        s.connect((server, port))
        s.send("NICK %s\r\n" % nick)
        s.send("USER %s %s bla :%s\r\n" % (ident, server, realname))
        s.send("JOIN %s\r\n" % chan);

        while 1:
            readbuffer=readbuffer+s.recv(1024)
            temp=string.split(readbuffer, "\n")
            readbuffer=temp.pop( )

            for line in temp:
                line=string.rstrip(line)
                line=string.split(line)

                if(line[0]=="PING"):
                    s.send("PONG %s\r\n" % line[1])
                if len(line) > 4 and line[3] == chan and line[4] == ':End':
                    s.send("PRIVMSG %s :%s \r\n" %
                        (chan,
                         self.format(message, data, context))
                    )
                    sys.exit(0)
