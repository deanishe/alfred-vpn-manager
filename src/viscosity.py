#!/usr/bin/python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-09-01
#

"""viscosity.py (list|connect|disconnect) [<query>] [<name>]

Usage:
    viscosity.py list [<query>]
    viscosity.py connect [-a|--all] [<name>]
    viscosity.py disconnect [-a|--all] [<name>]
    viscosity.py -h

Options:
    -a, --all   Apply action to all connections.
    -h, --help  Show this message and exit.
"""

from __future__ import print_function, unicode_literals, absolute_import

from collections import namedtuple
from operator import attrgetter
import pipes
import subprocess
import sys

import docopt
from workflow import Workflow, ICON_WARNING

log = None


VPN = namedtuple('VPN', ['name', 'active'])


def run_script(script_name, *args):
    """Return output of script `script_name`.


    Script must reside in `./scripts` subdirectory and
    have extension `.scpt`.

    """

    script = wf.workflowfile('scripts/{0}.scpt'.format(script_name))
    cmd = ['/usr/bin/osascript', script.encode('utf-8')]
    cmd += [a.encode('utf-8') for a in args]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError('Script `{0}` returned {1}'.format(
                           script, proc.returncode))
    output = wf.decode(proc.stdout.read())
    log.debug('Script : %r', script)
    log.debug('Output : %r', output)
    return output


def _load_connections():
    """Return list of VPN connections.

    Returns a list of VPN tuples.

    """

    connections = []
    output = run_script('get_connections').strip()
    for line in output.split('\n'):
        if '\t' not in line:
            log.warning('Bad line : %r', line)
            continue
        name, status = line.split('\t')
        if status == 'Connected':
            status = True
        else:
            status = False
        vpn = VPN(name, status)
        connections.append(vpn)
        log.info(vpn)

    connections.sort(key=attrgetter('name'))

    return connections


def load_connections():
    """Return list of VPN connections. Cache list for 5 seconds."""
    return wf.cached_data('connections', _load_connections, max_age=5)


def do_list(args):
    """Show/filter list of VPN connections."""
    query = args.get('<query>')

    icon_unlocked = wf.workflowfile('unlocked.png')

    connections = load_connections()

    active_connections = [c for c in connections if c.active]

    if len(active_connections) > 0:
        connected = True

    connected = False

    # ---------------------------------------------------------
    # Display active connections at the top if there's no query
    if not query:

        if len(active_connections) > 1:
            wf.add_item(
                'Disconnect All',
                'Action this item to close all connections',
                arg='disconnect --all',
                valid=True,
            )

        for con in active_connections:
            arg = 'disconnect {0}'.format(pipes.quote(con.name))
            wf.add_item(
                con.name,
                '↩ to disconnect',
                arg=arg,
                valid=True,
            )

    # ---------------------------------------------------------
    # Filter inactive connections
    if query:
        connections = wf.filter(query, connections, attrgetter('name'),
                                min_score=30)

    if not connections:
        wf.add_item('No matching connections.',
                    icon=ICON_WARNING)

    # ---------------------------------------------------------
    # Display inactive connections
    for con in connections:
        if con.active:
            continue

        arg = 'connect {0}'.format(pipes.quote(con.name))
        # Only add UID if there are no connected VPNs
        # to ensure connected VPNs are shown first
        if connected:
            uid = con.name
        else:
            uid = None
        wf.add_item(
            con.name,
            '↩ to connect',
            uid=uid,
            arg=arg,
            valid=True,
            icon=icon_unlocked,
        )

    wf.send_feedback()


def filter_connections(active=False, name=None):
    """Return list of connections by status and optionally by name."""
    connections = load_connections()
    connections = [c for c in connections if c.active == active]
    if name is not None:
        connections = [c for c in connections if c.name == name]
    return connections


def do_connect(args):
    """Connect to specified VPN(s)."""
    name = args.get('<name>')
    connections = filter_connections(False, name)
    for con in connections:
        log.debug('Connecting `%s` ...', con.name)
        run_script('connect_vpn', con.name)


def do_disconnect(args):
    """Disconnect specified VPN(s)."""
    name = args.get('<name>')
    connections = filter_connections(True, name)
    for con in connections:
        log.debug('Disconnecting `%s` ...', con.name)
        run_script('disconnect_vpn', con.name)


def main(wf):
    """Run workflow."""
    args = docopt.docopt(__doc__, wf.args,
                         version=wf.version)

    log.debug('args : %r', args)

    if args.get('list'):
        return do_list(args)
    elif args.get('connect'):
        return do_connect(args)
    elif args.get('disconnect'):
        return do_disconnect(args)
    else:
        raise ValueError('Unknown Action')


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
