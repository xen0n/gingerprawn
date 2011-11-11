#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.univlib.jiangnan / GeoIP-like IP-to-dorm converter
# XXX This file is to be moved to backend as its functionality can be shared
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

from os.path import realpath, split as pathsplit
from os.path import join as pathjoin

DATA_FILE = realpath(pathjoin(pathsplit(__file__)[0], 'dorms.txt'))
DATA_ENC = 'utf-8-sig'

SEGTYPE_FIELD = u'segtype'
# now the parsing of individual parts uses dynamic dispatch
SEGTYPE_UNIFORM = u'uniform'
SEGTYPE_SPECIAL = u'special'
# lambdas are used to prevent scoping error
SEGTYPE_DISPATCH = {SEGTYPE_UNIFORM: lambda a, b, c: parse_uniform(a, b, c),
                    SEGTYPE_SPECIAL: lambda a, b, c: parse_special(a, b, c),
                    }

IPPREFIX_FIELD = u'ipprefix'
IP_BEGIN_FIELD = u'ipsubstart'
IP_STEP_FIELD = u'ipstep'
APARTMENT_START_FIELD = u'apartmentstart'
DATALINE_PREFIX = u'"'

# NOTE: comment support seems to be superfluous due to internal mechanism
# which automatically ignores lines w/o '=' or a dataline prefix.
# But this feature enables you to comment datalines.
LINECOMMENT_DELIM = u'--'

__LOOKUP_TABLE = None

def __not_initialized_err(*args, **kwargs):
    raise RuntimeError("lookup table not initialized")
lookup = __not_initialized_err

def parse_parts(parts, dic=None):
    if dic is None:
        do_return = True
        dic = {}
    else:
        do_return = False

    for part in parts:
        # lines = [l for l in part.split('\n') if l]
        props = dict([l.split('=', 1) for l in part if '=' in l])
        data = [l[1:].split(',') for l in part if l[0] == DATALINE_PREFIX]

        # common to both types of segments, ipprefix is processed outside
        # the individual parser fn's.
        ipprefix = tuple([int(s) for s in props[IPPREFIX_FIELD].split('.')])
        segtype = props[SEGTYPE_FIELD]

        try:
            dic[ipprefix][segtype] = {}
        except KeyError:
            dic[ipprefix] = {segtype: {}, }
        curdic = dic[ipprefix][segtype]

        # dispatch work
        try:
            SEGTYPE_DISPATCH[segtype](props, data, curdic)
        except KeyError:
            # upwards compatibility: when encountering unknown segtype,
            # just ignore it and go on
            pass

    if do_return:
        return dic
    return

def parse_uniform(props, data, dic):
    subrange = int(props[IP_BEGIN_FIELD])
    delta = int(props[IP_STEP_FIELD])
    aptstart = int(props[APARTMENT_START_FIELD])

    # store some metadata to help seeking
    dic[IP_BEGIN_FIELD] = subrange
    dic[IP_STEP_FIELD] = delta
    dic[APARTMENT_START_FIELD] = aptstart
    # placeholder not needed, since apt no. is subtracted by aptstart
    # first.
    dic['data'] = []
    curlst = dic['data']

    for apt_name, num_apts_str, gender in data:
        num_apts = int(num_apts_str)
        genderchar = gender[0] if gender else u'' # FIXED: str type consistency
        curlst += [(apt_name, apt_no, genderchar, )
                for apt_no in range(aptstart, aptstart + num_apts)]
        aptstart += num_apts

def parse_special(props, data, dic):
    dic['data'] = {}
    curmap = dic['data']

    for apt_name, apt_no, ip_start, ip_end, gender in data:
        genderchar = gender[0] if gender else u'' # FIXED: str type consistency
        curmap[(int(ip_start), int(ip_end), )] = (apt_name, int(apt_no),
                genderchar, )

def read_in(fname):
    fp = open(fname, 'rb')
    raw_data = fp.read()
    fp.close()

    u_data = unicode(raw_data, DATA_ENC)
    # added comment support
    # so elaborate this a little bit
    rawlines = u_data.replace('\r\n', '\n').split('\n')
    comment_indices = [l.find(LINECOMMENT_DELIM) for l in rawlines]

    lines = [l if cidx == -1 else l[:cidx] 
                 for l, cidx in zip(rawlines, comment_indices)]
    data_w_o_comment = '\n'.join(lines)
    return [p
                for p in [[l for l in part_chunk.split('\n') if l]
                              for part_chunk in data_w_o_comment.split('\n\n')]
                if p
            ]

def init_lookup(fname=DATA_FILE):
    global __LOOKUP_TABLE
    global lookup
    __LOOKUP_TABLE = parse_parts(read_in(fname))
    lookup = _lookup

def _lookup(ip_tuple):
    # FIXED: returns None if list is passed in
    ip_tuple = tuple(ip_tuple)

    for prefix in __LOOKUP_TABLE:
        if ip_tuple[:len(prefix)] == prefix:
            subset = __LOOKUP_TABLE[prefix]
            ip_tuple = ip_tuple[len(prefix):]
            break
    try:
        subset
    except NameError:
        return None

    for segtype, seg in subset.items():
        if segtype == SEGTYPE_UNIFORM:
            # Uniform distribution, use accelerated indexing
            # Pull out the metadata stored during initialization.
            subrange = seg[IP_BEGIN_FIELD]
            delta = seg[IP_STEP_FIELD]

            try:
                return seg['data'][(ip_tuple[0] - subrange) / delta]
            except IndexError:
                pass # we put off failure return in case special branch has it
        elif segtype == SEGTYPE_SPECIAL:
            # We need to (at present) walk through the list.
            for ip_start, ip_end in seg['data']:
                if ip_start <= ip_tuple[0] <= ip_end: # Hit!
                    return seg['data'][(ip_start, ip_end, )]
            # put off failure detection
    # If we arrive here, our search has certainly failed.
    # Admit failure.
    return None

if __name__ == '__main__':
    init_lookup()
    prompt = 'ip addr, empty line to end: '

    while True:
        # hack to allow shorter input~
        m = raw_input(prompt).replace('*', '172')
        if not m:
            break
        ip = m.split('.')
        if len(ip) != 4:
            print 'incorrect address format'
            continue
        try:
            ip = tuple([int(i) for i in ip])
        except ValueError:
            print 'invalid char in address'
            continue
        if not all(0<=i<=255 for i in ip):
            print 'number too large or small'
            continue

        result = lookup(ip)
        if result is None:
            print 'not found in mapping'
        else:
            print u'%s %d# %s' % result


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8 ff=unix
