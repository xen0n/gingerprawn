#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.net / iface manipulator for linux2 platform
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

from subprocess import Popen, PIPE

import netinfo as info

from net_common import is_in_subnet
from net_common import ip2str, str2ip
from net_common import chk_ip_sanity
# from net_common import find_1st_match_ip, get_public_ip

# route command usage suggested by the blog article below
# http://blog.csdn.net/yangdaliang/archive/2010/06/08/5657000.aspx

__all__ = ['get_gateway',
           'get_ip',
           'get_public_gateway',
           'add_route',
           'del_route',
           ]

SETTING_COMMON = 'net %(subnet)s netmask %(mask)s gw %(gateway)s'
ROUTE_ADD_CMDLINE = 'route add -' + SETTING_COMMON
ROUTE_DEL_CMDLINE = 'route del -net %(subnet)s netmask %(mask)s'
PERMANENT_ROUTE_ENTRY = 'any ' + SETTING_COMMON

def get_gateway():
    route_tbl = info.get_routes()
    return tuple([i['gateway'] for i in route_tbl if i != '0.0.0.0'])

def get_ip():
    return tuple([info.get_ip(iface) for iface in info.list_active_devs()])

def get_public_gateway(subnet=None, netmask='255.255.255.0'):
    if (subnet is not None) and (netmask is not None):
        ips = [ip for ip in get_ip() if is_in_subnet(ip, subnet, netmask)]
    else:
        ips = get_ip()
    gws = get_gateway()
    result = []
    for ip in ips:
        for gw in gws:
            if is_in_subnet(gw, ip, netmask):
                result.append(gw)
    return tuple(result)

################################
def parse_route_cmd(out, err, retcode):
    if retcode == 0:
        return True
    raise OSError(err.strip('\n'))

def add_route(subnet, netmask, gateway, permanent=False):
    if permanent:
        raise NotImplementedError
    else:
        subp = Popen(args=(ROUTE_ADD_CMDLINE %
                {'subnet': ip2str(subnet),
                 'mask': ip2str(netmask),
                 'gateway': ip2str(gateway),
                 }).split(' '), stdout=PIPE, stderr=PIPE)
        out, err = subp.communicate()
        return parse_route_cmd(out, err, subp.returncode)

def del_route(subnet, netmask): # netmask a must in linux2 targets
    chk_ip_sanity(subnet)
    chk_ip_sanity(netmask)
    subp = Popen(args=(ROUTE_DEL_CMDLINE % {
            'subnet': ip2str(subnet),
            'mask': ip2str(netmask),
            }).split(' '),
            stdout=PIPE, stderr=PIPE)
    out, err = subp.communicate()
    return parse_route_cmd(out, err, subp.returncode)

# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
