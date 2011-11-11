#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.utils / metaprogramming and other dynamic stuff
# the snippets are originally inspired by a StackOverflow question, IIRC
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
import types

import inspect
outerframes = inspect.getouterframes
curframe = inspect.currentframe

def get_parent_frame(lvl):
    return outerframes(curframe())[lvl + 1]

def get_parent_globals(lvldelta=0):
    return get_parent_frame(1 + lvldelta)[0].f_globals

def get_parent_locals(lvldelta=0):
    return get_parent_frame(1 + lvldelta)[0].f_locals

def get_modname(lvldelta=0):
    return get_parent_globals(1 + lvldelta)['__name__']

def dynload(qualname):
    __import__(qualname)
    return sys.modules[qualname]

def fun2meth(func, obj, name=None):
    obj.__dict__[func.func_name if name is None
                 else name] = methodize(func, obj)

def methodize(func, obj):
    '''\
    This helper returns the method-ized version of the function given.
    '''
    return types.MethodType(func, obj, obj.__class__)


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
