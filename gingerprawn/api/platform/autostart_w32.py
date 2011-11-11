#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.platform / autostart - win32 support
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

import _winreg as _reg

_RUN_KEY_PATH = r'Software\Microsoft\Windows\CurrentVersion\Run'

_VALUE_NAME = 'GingerprawnAutorun'
# Compose this value only once
_AUTOSTART_CMDLINE = '"%s" -A' % _APP_EXECUTABLE

def open_runkey(privilege=_reg.KEY_READ):
    '''\
    Convenient decorator for writing functions in this module.
    '''
    def __open_runkey_decorator(fn):
        def __wrapper(*args, **kwargs):
            with _reg.OpenKey(_reg.HKEY_CURRENT_USER, _RUN_KEY_PATH,
                    0, privilege) as key:
                return fn(key, *args, **kwargs)
        return __wrapper
    return __open_runkey_decorator

@open_runkey()
def query_autostart_status(key):
    try:
        val, typ = _reg.QueryValueEx(key, _VALUE_NAME)
    except WindowsError, e:
        # Investigate further...
        if e.errno == 2:
            # non-existent value (at least it is the value i get when i try
            # to access a non-existent value). it's OK to say False
            return False
        else:
            # sth errorneous happened, re-raise
            raise

    if typ == _reg.REG_SZ and val == _AUTOSTART_CMDLINE:
        # Both the type and value is correct, we're properly set up.
        return True
    else:
        return False

# These two functions actually takes no parameter, but to accept key object
# from decorator there must be one. Don't be misled.

@open_runkey(_reg.KEY_READ | _reg.KEY_SET_VALUE)
def _set_autostart(key):
    _reg.SetValueEx(key, _VALUE_NAME, 0, _reg.REG_SZ, _AUTOSTART_CMDLINE)

@open_runkey(_reg.KEY_READ | _reg.KEY_SET_VALUE)
def _unset_autostart(key):
    try:
        _reg.DeleteValue(key, _VALUE_NAME)
    except WindowsError, e:
        if e.errno == 2:
            # non-existent value, ignore the error
            pass
        else:
            raise

def set_autostart_status(new_stat):
    if new_stat:
        _set_autostart()
    else:
        _unset_autostart()


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
