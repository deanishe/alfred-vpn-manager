#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-09-01
#

"""vpn.py (list|connect|disconnect|app) [<query>] [<name>]

Usage:
    vpn.py list [<query>]
    vpn.py connect [-a|--all] [<name>]
    vpn.py disconnect [-a|--all] [<name>]
    vpn.py app <name>
    vpn.py conf [<query>]
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
from operator import attrgetter, itemgetter
import sys
from time import time

import docopt
from workflow import Workflow3, ICON_WARNING, ICON_WEB
from workflow.util import appinfo, run_command

log = None

ICON_CONNECTED = 'icons/locked.png'
ICON_DISCONNECTED = 'icons/unlocked.png'
ICON_CONFIG = 'icons/config.png'
ICON_DOCS = 'icons/docs.png'
ICON_HELP = 'icons/help.png'
ICON_ISSUE = 'icons/issue.png'
ICON_UPDATE_AVAILABLE = 'icons/update-available.png'
ICON_UPDATE_OK = 'icons/update-ok.png'

DOCS_URL = 'https://github.com/deanishe/alfred-viscosity/blob/master/README.md'
FORUM_URL = ('https://www.alfredforum.com/topic/'
             '7333-viscosity-vpn-connection-manager/')
ISSUES_URL = 'https://github.com/deanishe/alfred-viscosity/issues'

UPDATE_SETTINGS = {
    'github_slug': 'deanishe/alfred-viscosity'
}

# VPN configuration
VPN = namedtuple('VPN', ['name', 'active'])


# dP                dP
# 88                88
# 88d888b. .d8888b. 88 88d888b. .d8888b. 88d888b. .d8888b.
# 88'  `88 88ooood8 88 88'  `88 88ooood8 88'  `88 Y8ooooo.
# 88    88 88.  ... 88 88.  .88 88.  ... 88             88
# dP    dP `88888P' dP 88Y888P' `88888P' dP       `88888P'
#                      88
#                      dP


class NotInstalled(Exception):
    """Raised if an application is not installed."""


@contextmanager
def timed(name=None):
    """Context manager that logs execution time."""
    name = name or ''
    start_time = time()
    yield
    log.debug('[%0.2fs] %s', time() - start_time, name)


# dP   .dP 88d888b. 88d888b.    .d8888b. 88d888b. 88d888b. .d8888b.
# 88   d8' 88'  `88 88'  `88    88'  `88 88'  `88 88'  `88 Y8ooooo.
# 88 .88'  88.  .88 88    88    88.  .88 88.  .88 88.  .88       88
# 8888P'   88Y888P' dP    dP    `88888P8 88Y888P' 88Y888P' `88888P'
#          88                            88       88
#          dP                            dP       dP

class VPNApp(object):
    """Base class for application classes."""

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """Create new initialised `VPNApp`."""
        self._info = False

    @abc.abstractproperty
    def program(self):
        """Command to call to manipulate application."""

    @abc.abstractproperty
    def download_url(self):
        """URL to get application."""
        return

    @abc.abstractproperty
    def connections(self):
        """All VPN connections."""
        return

    @property
    def info(self):
        """Return application info or `None` if not installed."""
        if self._info is False:
            self._info = appinfo(self.name)
            log.debug('[%s] appinfo=%r', self.name, self._info)
        return self._info

    @property
    def installed(self):
        """Return `True` if application is installed."""
        return self.info is not None

    @property
    def selected(self):
        """Return `True` if this is the currently configured app."""
        return os.getenv('VPN_APP') == self.name

    @property
    def name(self):
        """Name of application."""
        return self.__class__.__name__

    def connect(self, name):
        """Connect to named VPN."""
        connections = self.filter_connections(name=name, active=False)
        for c in connections:
            log.info(u'connecting "%s" ...', c.name)

            cmd = self.program + ['connect', c.name]
            run_command(cmd)

    def disconnect(self, name):
        """Disconnect from named VPN."""
        connections = self.filter_connections(name=name, active=True)
        for c in connections:
            log.info(u'disconnecting "%s" ...', c.name)

            cmd = self.program + ['disconnect', c.name]
            run_command(cmd)

    def disconnect_all(self):
        """Disconnect from all VPNs."""
        connections = self.filter_connections(active=True)
        for c in connections:
            self.disconnect(c.name)

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

    @property
    def program(self):
        """Command for viscosity.js script."""
        return ['/usr/bin/osascript', '-l', 'JavaScript',
                wf.workflowfile('scripts/viscosity.js')]

    @property
    def download_url(self):
        """URL to get application."""
        return 'https://www.sparklabs.com/viscosity/'

    @property
    def connections(self):
        """All Viscosity VPN connections."""
        return wf.cached_data('viscosity-connections',
                              self._fetch_connections,
                              max_age=0, session=True)

    def _fetch_connections(self):
        """Get configurations from VPN app."""
        connections = []
        with timed('fetched Viscosity VPN connections'):
            cmd = self.program + ['list']

            data = json.loads(run_command(cmd))

            for t in data.items():
                connections.append(VPN(*t))

        return connections


class Tunnelblick(VPNApp):
    """Interface to Tunnelblick.app."""

    @property
    def program(self):
        """Command for tunnelblick.applescript."""
        return ['/usr/bin/osascript',
                wf.workflowfile('scripts/tunnelblick.applescript')]

    @property
    def download_url(self):
        """URL to get application."""
        return 'https://tunnelblick.net'

    @property
    def connections(self):
        """All Tunnelblick VPN connections."""
        return wf.cached_data('tunnelblick-connections',
                              self._fetch_connections,
                              max_age=0, session=True)

    def _fetch_connections(self):
        """Get configurations from VPN app."""
        connections = []
        with timed('fetched Tunnelblick VPN connections'):
            cmd = self.program + ['list']

            output = wf.decode(run_command(cmd)).strip()

            for line in output.split('\n'):
                active = True if line[0] == '1' else False
                name = line[2:]
                connections.append(VPN(name, active))

        return connections

    def disconnect_all(self):
        """Close all active VPNs."""
        cmd = self.program + ['disconnect-all']
        run_command(cmd)


def get_app():
    """Return application object for currently-selected app."""
    name = os.getenv('VPN_APP') or 'Viscosity'

    for cls in VPNApp.__subclasses__():
        if cls.__name__ == name:
            app = cls()
            if not app.installed:
                raise NotInstalled('Application "{}" is not installed'
                                   .format(app.name))

            return app

    raise ValueError('Unknown VPN app: ' + name)


def get_all_apps():
    """Return all application objects."""
    apps = []
    for cls in VPNApp.__subclasses__():
        apps.append(cls())

    apps.sort(key=attrgetter('name'))
    return apps


#                            .8888b oo
#                            88   "
# .d8888b. .d8888b. 88d888b. 88aaa  dP .d8888b.
# 88'  `"" 88'  `88 88'  `88 88     88 88'  `88
# 88.  ... 88.  .88 88    88 88     88 88.  .88
# `88888P' `88888P' dP    dP dP     dP `8888P88
#                                           .88
#                                       d8888P

def show_update():
    """Add an 'update available!' item."""
    if wf.update_available:
        wf.add_item('Workflow Update Available!',
                    u'↩ or ⇥ to install update',
                    autocomplete='workflow:update',
                    valid=False,
                    icon=ICON_UPDATE_AVAILABLE)
        return True

    return False


def do_config(query):
    """Show workflow configuration."""
    items = []

    # ------------------------------------------------------
    # Update status
    title = 'Workflow Is up to Date'
    icon = ICON_UPDATE_OK
    if wf.update_available:
        title = 'Workflow Update Available!'
        icon = ICON_UPDATE_AVAILABLE

    items.append(dict(
        title=title,
        subtitle=u'↩ or ⇥ to install update',
        autocomplete='workflow:update',
        valid=False,
        icon=icon,
    ))

    # ------------------------------------------------------
    # VPN apps
    for app in get_all_apps():
        if app.selected and app.installed:
            items.append(dict(
                title=u'{} (active)'.format(app.name),
                subtitle=u'{} is the active application'.format(app.name),
                icon=app.info.path,
                icontype='fileicon',
                valid=False,
            ))
        else:
            if app.installed:
                items.append(dict(
                    title=u'{}'.format(app.name),
                    subtitle=u'↩ to use {}'.format(app.name),
                    icon=app.info.path,
                    icontype='fileicon',
                    arg='app:' + app.name,
                    valid=True,
                ))
            else:
                items.append(dict(
                    title=u'{} (not installed)'.format(app.name),
                    subtitle=u'↩ to get {}'.format(app.name),
                    icon=ICON_WEB,
                    arg=app.download_url,
                    valid=True,
                ))

    # ------------------------------------------------------
    # URLs
    items.append(dict(
        title='Online Docs',
        subtitle='Open workflow docs in your browser',
        arg=DOCS_URL,
        valid=True,
        icon=ICON_DOCS,
    ))

    items.append(dict(
        title='Get Help',
        subtitle='Open AlfredForum.com thread in your browser',
        arg=FORUM_URL,
        valid=True,
        icon=ICON_HELP,
    ))

    items.append(dict(
        title='Report Problem',
        subtitle='Open GitHub issues in your browser',
        arg=ISSUES_URL,
        valid=True,
        icon=ICON_ISSUE,
    ))

    # ------------------------------------------------------
    # Filter and display results
    if query:
        items = wf.filter(query, items, itemgetter('title'),
                          min_score=30)

    if not items:
        wf.add_item('No Matches', 'Try a different query?',
                    icon=ICON_WARNING)

    for item in items:
        wf.add_item(**item)

    wf.send_feedback()


#                                                         dP
#                                                         88
# .d8888b. .d8888b. 88d888b. 88d888b. .d8888b. .d8888b. d8888P
# 88'  `"" 88'  `88 88'  `88 88'  `88 88ooood8 88'  `""   88
# 88.  ... 88.  .88 88    88 88    88 88.  ... 88.  ...   88
# `88888P' `88888P' dP    dP dP    dP `88888P' `88888P'   dP

def do_list(query):
    """Show/filter list of VPN connections."""
    try:
        app = get_app()
    except NotInstalled as err:
        wf.add_item(err.message,
                    'Use "vpnconf" to change the application',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return

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

        nouids = show_update()

        if len(active_connections) > 1:
            it = wf.add_item(
                'Disconnect All',
                'Action this item to close all connections',
                arg='--all',
                valid=True,
                icon=ICON_CONNECTED,
            )
            it.setvar('action', 'disconnect')

        for con in active_connections:
            it = wf.add_item(
                con.name,
                '↩ to disconnect',
                arg=con.name,
                valid=True,
                icon=ICON_CONNECTED,
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
            icon=ICON_DISCONNECTED,
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


def do_app(name):
    """Set VPN client application."""
    wf.setvar('VPN_APP', name, persist=True)


#          dP oo
#          88
# .d8888b. 88 dP
# 88'  `"" 88 88
# 88.  ... 88 88
# `88888P' dP dP

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

    elif args['conf']:
        return do_config(args.get('<query>'))

    elif args['app']:
        return do_app(args.get('<name>'))

    else:
        raise ValueError('unknown action')


if __name__ == '__main__':
    wf = Workflow3(update_settings=UPDATE_SETTINGS)
    log = wf.logger
    sys.exit(wf.run(main))
