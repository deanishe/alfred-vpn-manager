#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-09-01
#

"""vpn.py (list|connect|disconnect) [<query>] [<name>]

Usage:
    vpn.py list [<query>]
    vpn.py connect [-a|--all] [<name>]
    vpn.py disconnect [-a|--all] [<name>]
    vpn.py -h

Options:
    -a, --all   Apply action to all connections.
    -h, --help  Show this message and exit.
"""

from __future__ import print_function, absolute_import

import abc
from collections import namedtuple
from contextlib import contextmanager
import json
import os
from operator import attrgetter
import subprocess
import sys
from time import time

import docopt
from workflow import Workflow3, ICON_WARNING

log = None

ICON_UPDATE = 'update-available.png'
UPDATE_SETTINGS = {
    'github_slug': 'deanishe/alfred-viscosity'
}

VPN = namedtuple('VPN', ['name', 'active'])


@contextmanager
def timed(name=None):
    """Context manager that logs execution time."""
    name = name or ''
    start_time = time()
    yield
    log.debug('[%0.2fs] %s', time() - start_time, name)


class VPNApp(object):
    """Base class for application classes."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def connections(self):
        return

    def connect(self, name):
        """Connect to named VPN."""
        connections = self.filter_connections(name=name, active=False)
        for c in connections:
            log.info(u'connecting "%s" ...', c.name)

            cmd = self.program + ['connect', c.name]
            run_command(*cmd)

    def disconnect(self, name):
        """Disconnect from named VPN."""
        connections = self.filter_connections(name=name, active=True)
        for c in connections:
            log.info(u'disconnecting "%s" ...', c.name)

            cmd = self.program + ['disconnect', c.name]
            run_command(*cmd)

    @abc.abstractmethod
    def disconnect_all(self):
        """Disconnect all connected VPNs."""
        return

    def filter_connections(self, name=None, active=True):
        """Return connections with matching name and state."""
        connections = self.connections
        if name:
            connections = [c for c in connections if c.name == name]
        if active:
            connections = [c for c in connections if c.active]
        else:
            connections = [c for c in connections if not c.active]

        return connections


class Viscosity(VPNApp):
    """Interface to Viscosity.app."""

    def __init__(self):
        self.program = ['/usr/bin/osascript', '-l', 'JavaScript',
                        wf.workflowfile('viscosity.js')]

    @property
    def connections(self):
        """All Viscosity VPN connections."""
        return wf.cached_data('viscosity-connections',
                              self._fetch_connections,
                              max_age=0, session=True)

    def _fetch_connections(self):
        """Get configurations from VPN app."""
        connections = []
        with timed('fetched VPN connections'):
            cmd = self.program + ['list']

            data = json.loads(run_command(*cmd))

            for t in data.items():
                connections.append(VPN(*t))

        return connections

    def disconnect_all(self):
        """Disconnect from all VPNs."""
        connections = self.filter_connections(active=True)
        for c in connections:
            log.info(u'disconnecting "%s" ...', c.name)

            cmd = self.program + ['disconnect', c.name]
            run_command(*cmd)


class Tunnelblick(VPNApp):
    """Interface to Tunnelblick.app."""

    def __init__(self):
        self.program = ['/usr/bin/osascript',
                        wf.workflowfile('tunnelblick.applescript')]

    @property
    def connections(self):
        """All Tunnelblick VPN connections."""
        return wf.cached_data('tunnelblick-connections',
                              self._fetch_connections,
                              max_age=0, session=True)

    def _fetch_connections(self):
        """Get configurations from VPN app."""
        connections = []
        with timed('fetched VPN connections'):
            cmd = self.program + ['list']

            output = wf.decode(run_command(*cmd)).strip()

            for line in output.split('\n'):
                active = True if line[0] == '1' else False
                name = line[2:]
                connections.append(VPN(name, active))

        return connections

    def disconnect_all(self):
        """Close all active VPNs."""
        cmd = self.program + ['disconnect-all']
        run_command(*cmd)


def run_command(*args):
    """Run command and return output."""
    cmd = [s.encode('utf-8') for s in args]
    log.debug('cmd=%r', cmd)
    return subprocess.check_output(cmd)


def get_app():
    """Return application object for selected app."""
    name = os.getenv('VPN_APP') or 'Viscosity'

    for cls in VPNApp.__subclasses__():
        if cls.__name__ == name:
            return cls()

    raise ValueError('Unknown VPN app: ' + name)


def do_list(query):
    """Show/filter list of VPN connections."""
    ICON_UNLOCKED = wf.workflowfile('unlocked.png')

    app = get_app()

    connections = app.connections

    active_connections = [c for c in connections if c.active]

    if len(active_connections) > 0:
        connected = True
    else:
        connected = False

    # ---------------------------------------------------------
    # Display active connections at the top if there's no query
    nouids = False
    if not query:

        if wf.update_available:
            nouids = True
            wf.add_item('Update available!',
                        'Action this item to update the workflow',
                        autocomplete='workflow:update',
                        valid=False,
                        icon=ICON_UPDATE)

        if len(active_connections) > 1:
            it = wf.add_item(
                'Disconnect All',
                'Action this item to close all connections',
                arg='--all',
                valid=True,
            )
            it.setvar('action', 'disconnect')

        for con in active_connections:
            it = wf.add_item(
                con.name,
                '↩ to disconnect',
                arg=con.name,
                valid=True,
            )
            it.setvar('action', 'disconnect')

    # ---------------------------------------------------------
    # Filter inactive connections
    if query:
        with timed('filtered connections'):
            connections = wf.filter(query, connections, attrgetter('name'),
                                    min_score=30)

    if not connections:
        wf.add_item('No Matching Connections', 'Try a different query?',
                    icon=ICON_WARNING)

    # ---------------------------------------------------------
    # Display inactive connections
    for con in connections:
        if con.active:
            continue

        # Only add UID if there are no connected VPNs
        # to ensure connected VPNs are shown first
        if connected or nouids:
            uid = None
        else:
            uid = con.name

        it = wf.add_item(
            con.name,
            u'↩ to connect',
            uid=uid,
            arg=con.name,
            valid=True,
            icon=ICON_UNLOCKED,
        )
        it.setvar('action', 'connect')

    wf.send_feedback()


def do_connect(name):
    """Connect to specified VPN(s)."""
    app = get_app()
    app.connect(name)


def do_disconnect(name):
    """Disconnect specified VPN(s)."""
    app = get_app()
    app.disconnect(name)


def main(wf):
    """Run workflow."""
    args = docopt.docopt(__doc__, wf.args, version=wf.version)

    log.debug('args : %r', args)

    if args['list']:
        return do_list(args.get('<query>'))

    elif args['connect']:
        return do_connect(args.get('<name>'))

    elif args['disconnect']:
        return do_disconnect(args.get('<name>'))
    else:
        raise ValueError('unknown action')


if __name__ == '__main__':
    wf = Workflow3(update_settings=UPDATE_SETTINGS)
    log = wf.logger
    sys.exit(wf.run(main))
