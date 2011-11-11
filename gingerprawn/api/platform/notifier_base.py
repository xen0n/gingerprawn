#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.platform / base class for platform-specific Notifier
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

class NotifierBase(object):
    def __init__(self, appname, frameobj, *args,  **kwargs):
        self.__icon = None
        self.appname = appname
        # XXX Use weakref here, or let the descendant classes decide
        # for themselves?
        #
        # self.frame = frameobj

    def __del__(self):
        pass

    def get_icon(self):
        # this "protected" member is self._NotifierBase__icon actually...
        # so access to it must be within this base class
        return self.__icon

    def set_icon_from_file(self, filename, *args, **kwargs):
        if not filename:
            # empty the icon...
            self.__icon = None
        else:
            self._set_icon(filename, *args, **kwargs)

    def _do_set_icon(self, icon):
        self.__icon = icon

    def _set_icon(self, filename, *args, **kwargs):
        raise NotImplementedError

    def message(self, title, body, timeout, *args, **kwargs):
        raise NotImplementedError


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
