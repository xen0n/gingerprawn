#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.univlib.jiangnan / Jiangnan University support library
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

__all__ = ['UNIVERSITY_NAME',
           'UNIVERSITY_LOGO',
           'jwxt',
           'library',
           ]

UNIVERSITY_NAME = u'江南大学'
from jiangnan_logo import UNIVERSITY_LOGO

from gingerprawn.api import logger
logger.install()

logdebug('Jiangnan University support library')

# expose the subsystem interfaces, because the "current" variable
# won't be able to include the modules without these lines
from . import jwxt
from . import library
from . import curtime

# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
