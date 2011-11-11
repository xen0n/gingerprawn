#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / launcher / module path helper
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

__all__ = ['we_are_frozen',
           'module_path',
           ]

# Code used to help us determine executable path
# Mainly taken from http://www.py2exe.org/index.cgi/WhereAmI
# Retrieved 16:51 GMT+0800 2011-03-29.
#
# Update 20111023: fixed exception when _file passed into the two funcs
# is of type unicode.

import os
import sys

realpath = os.path.realpath
normpath = os.path.normpath
pathjoin = os.path.join
dirname = os.path.dirname

def we_are_frozen():
    """\
    Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located.
    """

    return hasattr(sys, "frozen")

# this attribute isn't going to change during one launch...
WE_ARE_FROZEN = hasattr(sys, "frozen")

def module_path(_file):
    """\
    This will get us the program's directory,
    even if we are frozen using py2exe
    """
    if WE_ARE_FROZEN:
        _file = sys.executable
    if not issubclass(type(_file), unicode):
        _file = unicode(_file, sys.getfilesystemencoding())

    return realpath(dirname(_file))

def executable_path(_file):
    '''\
    This will get us the program's real path,
    even if we are frozen using py2exe
    '''
    if WE_ARE_FROZEN:
        _file = sys.executable
    if not issubclass(type(_file), unicode):
        _file = unicode(_file, sys.getfilesystemencoding())

    return realpath(_file)


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
