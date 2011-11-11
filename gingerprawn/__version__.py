#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / main package / package version file
# NOTE: the SVN support code reused Django project's.
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

import os.path
import re
import gingerprawn

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_REV = 0

VERSION = (VERSION_MAJOR, VERSION_MINOR, VERSION_REV, 'alpha', 1)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = '%s %s %s' % (version, VERSION[3], VERSION[4])

    # VCS revision, if we are in an devel environment
    # updated to support Git too
    vcs_ok, vcs_rev = get_vcs_revision()
    if vcs_ok:
        # Update: when it's dev version, show no conventional version number
        version = vcs_rev
    return version

###############################################################
## for getting revision info from a VCS
###############################################################

VCS_HANDLERS = []

def get_vcs_revision(path=None):
    # try the handlers one by one, return the first successful
    # match of VCS info
    for handler in VCS_HANDLERS:
        is_ok, result = handler(path)
        if is_ok:
            return (is_ok, result, )

    # no info available, signal failure
    return (False, None, )

def get_svn_revision(path=None):
    """
    Returns the SVN revision in the form SVN-XXXX,
    where XXXX is the revision number.

    Returns (False, None) if anything goes wrong, such as an unexpected
    format of internal SVN files.

    If path is provided, it should be a directory whose SVN info you want to
    inspect. If it's not provided, this will use the root package
    directory.
    """
    rev = None
    if path is None:
        path = gingerprawn.__path__[0]
    entries_path = '%s/.svn/entries' % path

    try:
        entries = open(entries_path, 'r').read()
    except IOError:
        pass
    else:
        # Versions >= 7 of the entries file are flat text.  The first line is
        # the version number. The next set of digits after 'dir' is the revision.
        if re.match('(\d+)', entries):
            rev_match = re.search('\d+\s+dir\s+(\d+)', entries)
            if rev_match:
                rev = rev_match.groups()[0]
        # Older XML versions of the file specify revision as an attribute of
        # the first entries node.
        else:
            from xml.dom import minidom
            dom = minidom.parse(entries_path)
            rev = dom.getElementsByTagName('entry')[0].getAttribute('revision')

    if rev:
        return (True, u'SVN-%s' % rev, )
    return (False, None, )

VCS_HANDLERS.append(get_svn_revision)

# TODO: add Git revision fetching support
def get_git_commit(path=None):
    """
    Returns the Git commit id in the form Git-01234567,
    where the commit id is truncated after the 8th hex digit.

    Returns (False, None) if anything goes wrong, such as an unexpected
    format of internal Git files.

    If path is provided, it should be a directory whose Git info you want to
    inspect. If it's not provided, this will use the root package
    directory's parent dir.
    """
    commit_id = None
    if path is None:
        path = gingerprawn.__path__[0]
        loghead_path = '%s/../.git/logs/HEAD' % path
    else:
        loghead_path = '%s/.git/logs/HEAD' % path
    # normalize a little bit
    loghead_path = os.path.normpath(loghead_path)

    try:
        loghead = open(loghead_path, 'rb').read()
    except IOError:
        pass
    else:
        parts = loghead.split(' ')
        commit_id = parts[1][:8]

    if commit_id:
        return (True, u'Git-%s' % commit_id, )
    return (False, None, )

VCS_HANDLERS.append(get_git_commit)

# init our version str... this is constant during one run
VERSION_STR = get_version()


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
