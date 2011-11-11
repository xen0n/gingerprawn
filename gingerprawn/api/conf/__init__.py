#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.conf / unified configuration manager - functions
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

'''\
This module implements several configuration-related functions
meant for module-level use.

By extensive use of inspection, module names don't need to be
explicitly specified in the ``get_*`` methods.
'''

# XXX REMEMBER TO UPDATE THIS IF CHANGES ARE MADE!
__all__ = ['GingerprawnConfig',
           'CONF_DIR',
           'CONF_DIR_RELPATH',
           'get_conf_modname',
           'get_conf_filename',
           'get_conf',
           ]

import os
import sys

pathjoin = os.path.join
normpath = os.path.normpath

# use our custom parser
# import ConfigParser
from .cfgclass import GingerprawnConfig

from gingerprawn.api.utils.metaprogramming \
        import get_modname, get_parent_globals

# NOTE: here we wouldn't want to log any message, because the logger depends
# on this module to get its own configuration file.
# Originally I had attempted to import logger here but soon deleted the line.

CONF_DIR_RELPATH = './conf'
CONF_DIR = normpath(pathjoin(_PKG_TOPLEV, CONF_DIR_RELPATH))


def get_conf_modname(lvldelta=0):
    '''\
    Returns the module name of caller. Defaults to the direct caller,
    but this behavior can be changed by supplying appropriate *lvldelta*\ .
    '''
    modname = get_modname(1 + lvldelta)
    prnt_globals = get_parent_globals(1 + lvldelta)
    if '_main' == modname[-5:] and 'SHRIMP_INFO' in prnt_globals:
        # a shrimp, if programmed strictly according to the doc.
        # decorate this a little
        modname = 'shrimp-' + modname[:-5]

    return modname.replace('.', '-')

def get_conf_filename(version=None, ext='ini', lvldelta=0):
    '''\
    Compose a configuration filename for the caller module,

    File extension can be specified, defaults to ``'ini'``\ .

    Also optional is multiple possible configurations, distinguished
    by the *version* parameter, which gets reflected in the filename.

    Similar to ``get_conf_module`` (which is directly called inside),
    number of frames to backtrack can be overridden.
    '''
    # another damn frame, the python vm is too slow at invoking functions...
    modname = get_conf_modname(1 + lvldelta)
    if version is None:
        return pathjoin(CONF_DIR, '%s.%s' % (modname, ext, ))
    return pathjoin(CONF_DIR, '%s(%s).%s' % (modname, version, ext, ))

def get_conf(version=None, ext='ini', lvldelta=0):
    '''\
    Get a ``GingerprawnConfig`` object (which is compatible with
    ``SafeConfigParser``\ ) specially prepared for the caller module,
    the parameters having the same meanings as ``get_conf_filename``\ .
    '''
    parser = GingerprawnConfig(get_conf_filename(version, ext, 1 + lvldelta))
    return parser


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
