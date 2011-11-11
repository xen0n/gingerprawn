#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / launcher / entry point for Windows
# shebang line added, unused though
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

# indicate that we're in no-console mode, also help determine the correct
# path for invocation
import __builtin__

try:
    __builtin__.__dict__['_NOCONSOLE_FILE'] = __file__
except NameError:
    # here we're not going to really determine whether py2exe'd or not,
    # but from this lack of __file__ we can safely assume that the branch
    # needing __file__ in modpath.py (later invoked by main.py) is not
    # taken. Just give a dummy value.
    __builtin__.__dict__['_NOCONSOLE_FILE'] = None

import main
main.main()


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
