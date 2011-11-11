#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.univlib.jiangnan / Specific Library system backend
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

from gingerprawn.api.univlib.backends import library_libsys as _lib

ENTRY_URL = 'http://202.195.149.18:8888/reader/login.php'

class JiangnanLibrary(_lib.LibsysLibrary):
    def __init__(self, *args, **kwargs):
        _lib.LibsysLibrary.__init__(self, ENTRY_URL, *args, **kwargs)


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
