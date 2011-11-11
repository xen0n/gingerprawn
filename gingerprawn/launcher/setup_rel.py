#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / packaging / py2exe release config
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

from distutils.core import setup
import py2exe

from py2exe_cfg import py2exe_options

setup(
    name=u'江大侠',
    version=u'0.1.0', # hard coded, maybe fixed in next release...
    description=u'江大人自己的校园生活客户端 此版本为测试版',
    author=u'江大侠开发团队',
    windows=[{'script':'winmain.pyw',
                'icon_resources':[(1, 'main_exe_icon.ico', ), ], }, ],
    options={"py2exe": py2exe_options}
)


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
