# DCI Agent

The DCI agent is in charge of retrieving

## How it works

## Configuration

Before proceeding any further, the administrator of the platform on which
dci-agent is deployed needs to configure it accordingly.

The main configuration file is located at `/etc/dci_agent.conf` (This behavior
can be changed either by specifying `--config-file /path/to/file` or by
specifying the `DCI_AGENT_CONFIG` environment variable.

There are two main sections of configuration.

### auth

Those are the authentication related parameters.


| Parameter     | Description                           | Default                       |
| ------------- | ------------------------------------- | ----------------------------- |
| dci_login     | User login                            | Mandatory                     |
| dci_password  | User password                         | Mandatory                     |
| dci_cs_url    | DCI Control Server to authenticate to | https://api.distributed-ci.io |


### dci

Those are the agent workflow related parameters.

A sample configuration looks like the following:

```
dci:
  topic: TOPIC_ID
  remoteci: REMOTECI_ID
  new:
    - irc
    - email
  pre-run:
    - mirror-sync
  running:
    - ansible
  post-run:
    - tempest
  success:
    - irc
    - email
  failure:
    - irc
    - email
```

The administrator needs to specify the `topic_id` and the `remoteci_id` for
which this agent will be run. Administrator can retrieve those information
from the Control Server administration interface.

Then for each state the agent will go through (ie. 'new', 'pre-run', 'running',
'post-run', 'success', 'failure'), the administrator will state which plugin
should be called for any given step.

In the example above, a new email and IRC notification will be sent when the
job starts running, then before the main 'running' state the plugin mirror-sync
will be called, the main 'running' state consist of an ansible playbook run and
finally the tempest plugin will be run. Wether this pipeline was succesful or
failed an IRC notification and an email will be sent to the configured receivers.


| Parameter | Description                                             | Default   |
| --------- | ------------------------------------------------------- | --------- |
| topic     | Topic ID                                                | Mandatory |
| remoteci  | RemoteCI ID                                             | Mandatory |
| new       | Array of plugins to call when entering 'new' state      | N/A       |
| pre-run   | Array of plugins to call when entering 'pre-run' state  | N/A       |
| running   | Array of plugins to call when entering 'running' state  | N/A       |
| post-run  | Array of plugins to call when entering 'post-run' state | N/A       |
| success   | Array of plugins to call when entering 'success' state  | N/A       |
| failure   | Array of plugins to call when entering 'failure' state  | N/A       |


### Plugins

Each plugins are customizable and can provide their configuration within a
configuration file. One can add them directly in `/etc/dci_agent.conf` but it
is recommended to include them in `/etc/dci_agent.conf.d/<pluginname>.conf`

A sample configuration for the `file` plugin looks like the following:

```
file:
  path: /var/log/dci_agent_run.log
  new:
    message: (%r) A Run of DCI agent for %j is about to start (%c)
  pre-run:
    message: (%r) A Run of DCI agent for %j entered the 'pre-run' state (%c)
  running:
    message: (%r) A Run of DCI agent for %j entered the 'running' state (%c)
  post-run:
    message: (%r) A Run of DCI agent for %j entered the 'post-run' state (%c)
  success:
    message: (%r) A Run of DCI agent for %j has succesfully finished (%c)
  failure:
    message: (%r) A Run of DCI agent for %j has failed (%c)
```

When this plugin will be called for a given state, the matching message will be
written in the file `/var/log/dci_agent_run.log`

The same pattern applies for the others plugins.
