#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.net / iface manipulator for win32 platform
# NOTE: this module depends on the netinfo module
#
# Copyright (C) 2011 Wang Xuerui <idontknw.wang@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from subprocess import Popen, PIPE
import re

from operator import and_

from net_common import ip2str, str2ip
from net_common import chk_ip_sanity
from net_common import find_1st_match_ip, get_public_ip

__all__ = ['get_gateway',
           'get_public_gateway',
           'add_route',
           'del_route',
           ]

################################
# Gateway info retrieving
IPV4_PAT = r'(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
IPV6_PAT = r'(?:[0-9A-Fa-f:]+(?:%\d+)*)' # i don't have time to polish this up at present
ONEIP_CATCH_PAT = r'(%s|%s)' % (IPV4_PAT, IPV6_PAT, )

GATEWAY_PATS = (r'\xc4\xac\xc8\xcf\xcd\xf8\xb9\xd8[ .]+: (.*?)\r\n\r\n',
        # % IP_CATCH_PAT,
        r'Default Gateway[ .]+: (.*?)\r\n\r\n', #  % IP_CATCH_PAT,
                )

GATEWAY_CATCHERS = tuple([re.compile(p, re.DOTALL) for p in GATEWAY_PATS])
ONEIP_CATCHER = re.compile(ONEIP_CATCH_PAT)

################################
# Static route mapping
ROUTE_ADD_CMDLINE = 'route add %(perm)s %(subnet)s mask %(mask)s %(gateway)s'
ROUTE_DEL_CMDLINE = 'route delete %(subnet)s'

ROUTE_STATUS_OK = (' \xb2\xd9\xd7\xf7\xcd\xea\xb3\xc9!\r\n',
                   ' OK!\r\n',
                   )

ROUTE_STATUS_ERR = {
        ('',
         '\xc2\xb7\xd3\xc9\xcc\xed\xbc\xd3\xca\xa7\xb0\xdc: ' \
         '\xb2\xce\xca\xfd\xb4\xed\xce\xf3\xa1\xa3\r\n\r\n',
         ): ValueError('invalid parameter'),
        ('',
         'The route addition failed: The parameter is incorrect.\r\n\r\n',
         ): ValueError('invalid parameter'),
        ('The requested operation requires elevation.\r\n',
         '',
         ): WindowsError('elevation required'),
        ('\xc7\xeb\xc7\xf3\xb5\xc4\xb2\xd9\xd7\xf7\xd0\xe8\xd2\xaa' \
         '\xcc\xe1\xc9\xfd\xa1\xa3\r\n',
         '',
         ): WindowsError('elevation required'),
        }


def invoke_ipconfig():
    ipconfig = Popen('ipconfig', stdout=PIPE)
    stdout = ipconfig.communicate()[0]
    del ipconfig
    return stdout

def parse_gateway(mesg):
    result = []
    for catcher in GATEWAY_CATCHERS:
        gateway_lst = catcher.findall(mesg)
        if gateway_lst:
            ip_lines = gateway_lst[0]
            result = ONEIP_CATCHER.findall(ip_lines)
            break
    return result

__GATEWAY_CACHE = None
def get_gateway(cache=True):
    global __GATEWAY_CACHE
    if cache is True and __GATEWAY_CACHE is not None:
        # since result is a tuple with no mutable objects,
        # we can safely pass it around.
        return __GATEWAY_CACHE

    result = _get_gateway()
    if cache is True:
        __GATEWAY_CACHE = result
    return result

def get_public_gateway(cache=True):
    gws = get_gateway(cache)
    return str2ip(find_1st_match_ip(gws, get_public_ip(str)))

def _get_gateway():
    msg = invoke_ipconfig()
    result = parse_gateway(msg)
    if not result:
        raise RuntimeError('cannot retrieve gateway address')
    return tuple(result)

# parse output from 'route' command and raise exception appropriately.
def parse_route_cmd(out, err, retcode):
    for msg in ROUTE_STATUS_OK:
        if msg == out:
            return True
    # if we arrived here, we failed
    raise ROUTE_STATUS_ERR.get((out, err, ),
            WindowsError('stdout=%s stderr=%s retcode=%d' %
                (out.strip('\r\n'), err.strip('\r\n'), retcode, )))

# XXX Add UAC awareness here when free
def add_route(subnet, netmask, gateway, permanent=False):
    chk_ip_sanity(subnet)
    chk_ip_sanity(gateway)
    chk_ip_sanity(netmask)
    if permanent is True:
        perm = '-p'
    else:
        perm = ''
    # validation made later to "fix" TOCTTOU
    # (although by no means completely avoiding)
    subp = Popen(ROUTE_ADD_CMDLINE %
            {'perm': perm,
             'subnet': ip2str(subnet),
             'mask': ip2str(netmask),
             'gateway': ip2str(gateway),
             }, stdout=PIPE, stderr=PIPE)
    out, err = subp.communicate()
    return parse_route_cmd(out, err, subp.returncode)

def del_route(subnet, netmask=None):
    # netmask is not needed in Win32, but added that to ensure
    # interface compatibility w/ linux2 target where mask is needed
    # to manipulate a static route table entry.
    chk_ip_sanity(subnet)
    chk_ip_sanity(netmask)
    subp = Popen(ROUTE_DEL_CMDLINE % {'subnet': ip2str(subnet), },
            stdout=PIPE, stderr=PIPE)
    out, err = subp.communicate()
    return parse_route_cmd(out, err, subp.returncode)

# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
