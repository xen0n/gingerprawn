#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.platform / notification - notifier provider wrapper
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
    from notify_w32 import *
elif platform == 'linux2':
    from notify_linux2 import *
else:
    raise ImportError('System notification not ported to platform %s yet!'
            % platform)

# sanity test
if __name__ == '__main__':
    from time import sleep
    from sys import exit, stdout

    print u'creating notifier'
    notifier = Notifier(u'test_appname', None)
    print u'notifier object: %s' % repr(notifier)

    print u'emitting notification...',
    ret = notifier.message(u'非洲农业不发达', u'必须要用金坷垃', 20)

    if ret:
        print u'ok'
    else:
        print u'FAILED'
        exit(1)

    for sec in range(20):
        print (u'%d s\r' % sec),
        stdout.flush()
        sleep(1)
    print

    print u'cleaning up'
    del notifier


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
