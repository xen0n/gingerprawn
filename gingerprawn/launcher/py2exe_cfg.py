#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / packaging / py2exe common config
# common options for producing debug (w/ a console) and release (consoleless)
# Windows executables
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

py2exe_options = dict(
            optimize=2,
            compressed=True,  # Compress library.zip
            includes=[
                'gzip',
                'mechanize',
                'lxml',
                'lxml._elementpath',
                'lxml.html',

                'gingerprawn',
                'gingerprawn.api',
                'gingerprawn.api.conf',
                'gingerprawn.api.cooker',
                'gingerprawn.api.net',
                'gingerprawn.api.platform',
                'gingerprawn.api.platform.w32version',
                'gingerprawn.api.platform.w32msgs',
                'gingerprawn.api.platform.wxmsw_wndhook',
                'gingerprawn.api.platform.aero',
                'gingerprawn.api.platform.autostart',

                'gingerprawn.api.ui',
                'gingerprawn.api.ui.aboutbox',
                'gingerprawn.api.ui.statusbar',
                'gingerprawn.api.ui.dragablegrid',

                'gingerprawn.api.univlib.jiangnan',

                'gingerprawn.api.utils',

                'gingerprawn.shrimp.lobster.lobster_main',
                'gingerprawn.shrimp.academic.academic_main',
                'gingerprawn.shrimp.librarian.librarian_main',
                ],
            excludes=[
                '_ssl', '_sqlite3',
                'pyreadline', 'difflib', 'doctest',
                'pickle', # 'calendar' used by mechanize
                ],
            dll_excludes=[
                'API-MS-Win-Core-LocalRegistry-L1-1-0.dll',
                'API-MS-Win-Core-ProcessThreads-L1-1-0.dll',
                'API-MS-Win-Security-Base-L1-1-0.dll',
                'KERNELBASE.dll',
                'POWRPROF.dll',
                'pywintypes26.dll',
                'w9xpopen.exe',
                ],
)


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
