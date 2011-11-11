#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.update / bz2'd {,un}pickling of objects
# the code taken from one of my former projects, the liver-1 tieba.baidu.com
# post crawler aggregating one author's posts.
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

from cPickle import dumps, loads

from bz2 import compress, decompress

################################################################
## Operation on String Representations.

def bzdumps(obj, compress_level=9):
    return compress(dumps(obj), compress_level)

def bzloads(s):
    return loads(decompress(s))

def bzb64dumps(*args, **kwargs):
    return bzdumps(*args, **kwargs).encode('base64')

def bzb64loads(s):
    return bzloads(s.decode('base64'))

################################################################
## Operation on Files.

def bzdump(filename, obj, compress_level=9):
    with open(filename, 'wb') as fp:
        fp.write(bzdumps(obj, compress_level))

def bzload(filename):
    with open(filename, 'rb') as fp:
        return bzloads(fp.read())


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
