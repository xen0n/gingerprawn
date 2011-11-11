#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.cooker / shrimp loader
# TODO: rename this file to sth like "shrimpldr"
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

import sys
import os
# I want more control over importing so do it myself
from zipimport import zipimporter, ZipImportError
syspath = sys.path

# added the long-forgotten logging support
from gingerprawn.api import logger
logger.install()

# maj.min.rev
# FIXED: unified this variable with __version__.py's
from gingerprawn.__version__ import VERSION as _VERSION
__version__ = _VERSION[:3]

# for UI, icon manager added
from gingerprawn.api.cooker import iconmgr

entrymodule = '%s_main'

SHRIMP_LOADVARS = ('SHRIMP_MINVER',
                   'SHRIMP_INFO',
                   'SHRIMP_PLATFORM',
                   'SHRIMP_ICON', # added for UI need
                   'shrimp_init',
                   'shrimp_threadproc',
                   'shrimp_down',
                   )

SHRIMP_VARREFS = tuple(v.lower().replace('shrimp_', '', 1)
                           for v in SHRIMP_LOADVARS)
INTERNAL_NAME_MAP = dict(zip(SHRIMP_VARREFS,SHRIMP_LOADVARS))

# zipped zhrimp or plain source code?
ZIPPED_SHRIMP = _APP_OPTIONS.zipped_shrimp

if ZIPPED_SHRIMP:
    logdebug('Running Zipped shrimp')
else:
    logdebug('Running raw shrimp')

def load_vars(mod):
    try:
        return dict(zip(SHRIMP_VARREFS,
                        [getattr(mod, v) for v in SHRIMP_LOADVARS]
                        ))
    except AttributeError:
        logerror('this shrimp does not have all the required variables set')
        return None

def getprop(mod, internal_name):
    return getattr(mod, INTERNAL_NAME_MAP[internal_name])

def ldmod_zip(shrimp, pkgpath):
    # This relies on main.py's overriding default encoding to work
    # when path contains non-ASCII chars (e.g. Hanzi)
    importer = zipimporter(pkgpath)
    tmp = importer.load_module(entrymodule % shrimp)
    del importer
    return tmp

def ldmod_raw(shrimp, pkgpath):
    # this is a "from gingerprawn.shrimp.<name> import <name>_main"
    tmp = __import__('%s_main' % shrimp, 'gingerprawn.shrimp.%s' % shrimp)
    return tmp

def load(shrimp, pkgpath):
    '''If succeed, returns the shrimp module
    '''
    logdebug('trying to load shrimp \'%s\' from path \'%s\'', shrimp, pkgpath)
    syspath.insert(0, '')
    try:
        # to allow shrimp to have its own internal structure, sys.path
        # must be modified so the shrimp's archive has an entry
        syspath[0] = pkgpath
        # alternate way of importing shrimp is now possible
        if ZIPPED_SHRIMP:
            tmp = ldmod_zip(shrimp, pkgpath)
        else:
            tmp = ldmod_raw(shrimp, pkgpath)
    except ImportError:
        logexception("ImportError during load of shrimp '%s'", shrimp)
        return None
    except:
        logexception("unexpected failure during load of shrimp '%s'", shrimp)
        return None
    finally:
        del sys.path[0]

    m_vars = load_vars(tmp)
    if m_vars is None:
        return None

    # platform check
    platforms = m_vars['platform'] # to save space
    if 'all' not in platforms and sys.platform not in platforms:
        logerror('platform incompatible: supported %s', ', '.join(platforms))
        return None

    # version check
    if not check_ver(m_vars['minver']):
        logerror('unsupported, minver %s requested', `m_vars['minver']`)
        return None

    try:
        m_vars['init']()
    except KeyboardInterrupt: # maybe user wanna exit rapidly
        loginfo('user sent keyboard interrupt signal, exiting')
        raise
    except:
        # something out of control happened
        log.exception('unexpected failure')
        del tmp
        return None

    # register the icon in our image list
    # TODO: make this more robust
    # this is at present not very elegant
    iconmgr.add_icon(shrimp, m_vars['icon'])

    # we're done, return the module
    return tmp

# this function is provided in case version compatibility gets out of
# control so that a simple comaprison is not enough.
def check_ver(ver):
    # for now simply check whether gingerprawn's version is >= shrimp's.
    return __version__ >= ver

# vi:ai:et:ts=4 sw=4 sts=4 ff=unix
