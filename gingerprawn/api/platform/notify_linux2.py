#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.platform / notification - linux2 platform support
# NOTE: facilitates pynotify
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

import pynotify

# for Pixbuf
import gtk

# base class of notifier
from notifier_base import NotifierBase

# TODO: add support for initializing image from memory buffer

class GTKNotifier(NotifierBase):
    def __init__(self, appname, frameobj):
        if not pynotify.is_initted():
            pynotify.init(appname)
        NotifierBase.__init__(self, appname, frameobj)

    def __del__(self):
        pynotify.uninit()

    def _set_icon(self, filename):
        self._do_set_icon(gtk.gdk.pixbuf_new_from_file(filename))

    def message(self, title, body, timeout=15):
        note = pynotify.Notification(title, body)
        note.set_timeout(timeout)

        icon = self.get_icon()
        if icon is not None:
            note.set_icon_from_pixbuf(icon)

        return note.show()

# alias
Notifier = GTKNotifier


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
