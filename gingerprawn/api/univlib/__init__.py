#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.univlib / University-specific libraries -- loader
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

from gingerprawn.api import logger
logger.install()

from gingerprawn.api.utils.metaprogramming import dynload
from gingerprawn.api.utils.security import is_valid_modulename

current = None

current_modname = ''

# Set current university.
def set_current_univ(univ):
    global current
    global current_modname

    if univ == 'backends' or (not is_valid_modulename(univ)):
        raise ValueError('invalid module name')

    current = dynload('.'.join([__name__, univ, ]))
    # keep module name for possible future use
    current_modname = univ
    loginfo('Current university set to %s (%s)', univ,
            current.UNIVERSITY_NAME)


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
