#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.utils / popen wrapper and convenient output parsing module
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

import os
from subprocess import Popen, PIPE
import re

# TODO: Implement this when I have time! -- xenon
class Popener(Popen):
    def __init__(self, *args, **kwargs):
        if 'managed' in kwargs:
            pass


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
