#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.platform / autostart functionality provider wrapper
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

from sys import platform

if platform == 'win32':
    from autostart_w32 import *
elif platform == 'linux2':
    from autostart_linux2 import *
else:
    raise ImportError('Autostart functionality not ported for platform %s yet!'
            % platform)


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
