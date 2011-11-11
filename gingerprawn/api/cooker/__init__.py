#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.cooker / shrimp manager -- major coordinator part
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

# XXX REMEMBER TO UPDATE THIS IF INTERFACE IS CHANGED!!!
__all__ = ['SHRIMP_DIR',
           'SHRIMP_EXT',
           'SHRIMP_LIST',
           'SHRIMP_LOADSTATUS',
           'SHRIMP_MODULES',
           'SHRIMP_RUNNING',
           ] # this is expanded later on

# this is an abuse of decorator, automatically adding identifiers to __all__
def expose(fn):
    __all__.append(fn.func_name)
    return fn

import sys
import os
import threading

from .shrimpmgr import getprop as getp

pathjoin = os.path.join
isfile = os.path.isfile
isdir = os.path.isdir
fsenc = sys.getfilesystemencoding()

from gingerprawn.api import logger
logger.install()

# At the first invocation, cwd is pkg toplevel, so this will do
# No. Always use the initial toplevel since TOCTTOU condition could occur
# XXX It seems that a single 'u' prefix here turned all paths returned into
#     Unicode...
SHRIMP_DIR = os.path.normpath(pathjoin(_PKG_TOPLEV, u'./shrimp'))

# gingerprawn is free software, so it makes no sense to hide the users
# from the fact that shrimp are plain zip files containing code
SHRIMP_EXT = '.zip'

SHRIMP_LIST = []
SHRIMP_MODULES = {}

SHRIMP_RUNNING = {}
SHRIMP_LOADSTATUS = {}

# shrimp discovery also needs to use this piece of info
_ZIPPED_SHRIMP = _APP_OPTIONS.zipped_shrimp

########################################################################
## Shrimp discovery routines
########################################################################

def do_discovery_zip():
    for shrimp in os.listdir(SHRIMP_DIR):
        # eliminate svn dir if encountered
        if '.svn' == shrimp:
            continue

        shrimp_module = pathjoin(SHRIMP_DIR, shrimp, shrimp + SHRIMP_EXT)
        if isfile(shrimp_module):
            SHRIMP_LIST.append((shrimp, shrimp_module, ))

def do_discovery_raw():
    for shrimp in os.listdir(SHRIMP_DIR):
        # eliminate svn dir if encountered
        if u'.svn' == shrimp:
            continue

        shrimp_module = pathjoin(SHRIMP_DIR, shrimp)
        if isdir(shrimp_module):
            SHRIMP_LIST.append((shrimp, shrimp_module, ))

@expose
def do_discovery():
    global SHRIMP_LIST

    logdebug('listing shrimp directory')
    if _ZIPPED_SHRIMP:
        do_discovery_zip()
    else:
        do_discovery_raw()
    # due to python's dynamic nature, i won't let shrimplist be altered
    # after initialization
    SHRIMP_LIST = tuple(SHRIMP_LIST)

    if logisdebug():
        logdebug("discover: %s", ' '.join(shrimp
                for shrimp, dummy in SHRIMP_LIST))


#########################################################################
## Shrimp loading wrapper
#########################################################################

# here callback function is splash frame's shrimploading progress listener
@expose
def load_shrimp(callback, shrimpdict=SHRIMP_MODULES):
    total = float(len(SHRIMP_LIST))
    i = 0
    for shrimp, pkg in SHRIMP_LIST:
        callback('try', shrimp, (i * 100 / total))
        tmp = shrimpmgr.load(shrimp, pkg)
        if tmp is None:
            SHRIMP_LOADSTATUS[shrimp] = 'fail'
            callback('fail', shrimp)
        else:
            shrimpdict[shrimp] = tmp
            SHRIMP_LOADSTATUS[shrimp] = 'ok'
            callback('ok', shrimp)
        i += 1
    # when we're done the caller should be able to regain control since
    # these all are single-threaded.
    return

@expose
def get_shrimp_mod(shrimp):
    try:
        return SHRIMP_MODULES[shrimp]
    except KeyError:
        raise KeyError('no such shrimp')

@expose
def bring_up_shrimp(shrimp, args=('normal')):
    if logisdebug():
        logdebug("attempting to bring up shrimp '%s' with args %s",
                shrimp, `args`)
    if shrimp in SHRIMP_RUNNING:
        logerror('the shrimp requested is already running')
        raise ValueError('already running')

    mod = get_shrimp_mod(shrimp)
    threadproc = getp(mod, 'threadproc')
    t = threading.Thread(target=threadproc,
        args=(args, ),
        name=('Shrimp_' + shrimp)
        )
    t.start()
    SHRIMP_RUNNING[shrimp] = t

# this should be a blocking operation (for now)
@expose
def bring_down_shrimp(shrimp):
    logdebug("attempting to bring down shrimp '%s'", shrimp)

    if shrimp not in SHRIMP_RUNNING:
        logerror("can't bring down a non-running shrimp")
        raise ValueError('not running')

    mod = get_shrimp_mod(shrimp)
    getp(mod, 'down')()
    # TODO: better sync here
    assert not SHRIMP_RUNNING[shrimp].is_alive()
    SHRIMP_RUNNING.pop(shrimp)

@expose
def query_shutdown(shrimp=None):
    if shrimp is not None:
        # this means only that shrimp will be queried
        mod = get_shrimp_mod(shrimp)
        return getp(mod, 'down')(True) # just_querying=True

    # ask around
    running = SHRIMP_RUNNING.keys()
    if logisdebug():
        logdebug('starting shutdown query, running shrimp: %s',
                ', '.join(running))
    for shrimp in running:
        if not query_shutdown(shrimp):
            # one of those shrimp doesn't want to shut down
            return False
    # no veto, metashrimp can go on
    return True

@expose
def do_shutdown():
    from time import sleep
    loginfo('shutdown requested, terminating all shrimp')
    running = SHRIMP_RUNNING.keys()
    for shrimp in running:
        bring_down_shrimp(shrimp)

@expose
def do_autostart(queue):
    loginfo('autostart task, invoking all shrimp')
    ok_list = [sh for sh, stat in SHRIMP_LOADSTATUS.items()
               if stat == 'ok']
    for sh in ok_list:
        bring_up_shrimp(sh, ('autostart', queue, ))

########################################################################
## Shrimp property access
########################################################################

@expose
def get_minver(shrimp):
    '''\
    Gets the minimal version of gingerprawn needed to host *shrimp*\ .
    Returns a 3-tuple ``(major, minor, rev)`` that is of
    the same format as ``gingerprawn.VERSION``\ .
    '''
    return getp(get_shrimp_mod(shrimp), 'minver')

@expose
def get_platform(shrimp):
    '''\
    Returns a list of supported platforms for this shrimp.
    A value of ``'all'`` indicates that it supports all platforms supported
    by gingerprawn.
    '''
    return getp(get_shrimp_mod(shrimp), 'platform')

@expose
def get_info(shrimp, __CACHE={}):
    '''\
    Returns the ``SHRIMP_INFO`` object exposed by the shrimp.
    The objects are cached by means of default parameter, so never pass
    more than one parameter to this function.
    '''
    if __CACHE.has_key(shrimp):
        return __CACHE[shrimp]
    else:
        __CACHE[shrimp] = getp(get_shrimp_mod(shrimp), 'info')
        return __CACHE[shrimp]

@expose
def get_name(shrimp):
    '''\
    Returns the name of *shrimp*\ . Usually this is a Unicode string.
    '''
    return get_info(shrimp)['name']

@expose
def get_version(shrimp):
    '''\
    Returns the version string of *shrimp*\ . Usually this is a bytestring.
    '''
    return get_info(shrimp)['ver']

@expose
def get_authors(shrimp):
    '''\
    Returns the list of authors of *shrimp*\ . Usually this is a list of Unicode
    strings.
    '''
    return get_info(shrimp)['author']

@expose
def get_desc(shrimp):
    '''\
    Returns the description of shrimp. Usually this is a Unicode string.
    '''
    return get_info(shrimp)['desc']

@expose
def get_license(shrimp):
    '''\
    Returns the terms under which *shrimp* is licensed. Usually this is a
    Unicode string.
    '''
    return get_info(shrimp)['lic']

@expose
def get_copyright(shrimp):
    '''\
    Returns the copyright information of *shrimp*\ . Usually this is a Unicode
    string.
    '''
    return get_info(shrimp)['copyr']

#############################################################################
## DISCOVERY MOVED TO FUNCTIONS, SO INVOCATION MOVED TO END OF FILE
#############################################################################

## MODIFIED: to facilitate proper autodocumenting, this is protected
## UPDATE 20111023: shrimp no longer auto-discovered on import, discover
## manually on init.

#try:
#    # set up by an added line in doc/<LANG>/conf.py
#    _APP_OPTIONS._is_autodoc
#except AttributeError:
#    # is actually running as an app, do discovery
#    do_discovery()


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
