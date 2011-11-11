#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.platform / skeleton Windows version detection wrapper
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

__all__ = ['uname',
           'is_xp',
           'is_win7',
           ]

import platform

# the names are used instead of lambda's for sake of clarity...
def actually(name):
    def dummy():
        return True
    dummy.func_name = '_actually_%s' % name
    return dummy

def actually_not(name):
    def dummy():
        return False
    dummy.func_name = '_actually_not_%s' % name
    return dummy

uname = platform.uname()

if uname[0] == 'Windows':
    if uname[2] == 'XP':
        is_xp = actually('xp')
        is_win7 = actually_not('win7')
    elif uname[3][:3] == '6.1':
        is_xp = actually_not('xp')
        is_win7 = actually('win7')
else:
    is_xp = actually_not('xp')
    is_win7 = actually_not('win7')


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
