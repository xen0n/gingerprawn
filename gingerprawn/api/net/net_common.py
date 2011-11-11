#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.net / common net-related shortcut functions
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

import socket

from operator import and_, add

# XXX NOT IPv6 COMPATIBLE
def chk_ip_sanity(*ips):
    chk_ipv4_sanity(*ips)

def chk_ipv4_sanity(*ips):
    for ip in ips:
        if type(ip) is str:
            chk_ip_sanity(str2ip(ip))
            continue
        if len(ip) != 4:
            # return False
            flag = True
        if not reduce(and_, [type(i) is int for i in ip]):
            # return False
            flag = True
        if not reduce(and_, [0 <= i <= 255 for i in ip]):
            # return False
            flag = True
        try:
            flag
            raise ValueError('invalid IP address tuple')
        except NameError:
            pass
    return

def prune_ipv6(ips):
    result = []
    for ip in ips:
        try:
            chk_ipv4_sanity(ip)
            result += [ip]
        except ValueError:
            pass
    return result

def str2ip(ip_str):
    return tuple([int(i) for i in ip_str.split('.')])

def ip2str(ip, safe=False):
    if not safe:
        chk_ip_sanity(ip)

    if type(ip) is str:
        return ip
    return '.'.join([str(i) for i in ip])

def get_public_ip(typ=tuple):
    ipstr = socket.gethostbyname(socket.gethostname())
    if typ is str:
        return ipstr
    elif typ is tuple:
        return str2ip(ipstr)
    else:
        raise ValueError('invalid return type given')

def str2addr(ip):
    return socket.inet_aton(ip)

def addr2str(ip):
    return socket.inet_ntoa(ip)

def addr2int(addrstr):
    return reduce(add,
            [256 ** (3 - pos) * ord(byt) for pos, byt in enumerate(addrstr)])

def str2int(ipstr):
    return addr2int(str2addr(ipstr))

def is_in_subnet(ip1, ip2, netmask):
    ip1 = ip2str(ip1)
    ip2 = ip2str(ip2)
    netmask = ip2str(netmask)
    int1 = str2int(ip1)
    int2 = str2int(ip2)
    nm = str2int(netmask)
    return (int1 & nm) == (int2 & nm)

# XXX NOT IPv6 COMPATIBLE
def find_1st_match_ip(ips, tgt, netmask='255.255.255.0'):
    for ipstr in prune_ipv6(ips):
        if is_in_subnet(ipstr, tgt, netmask):
            return ipstr
    return None


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8

