#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.univlib.backends / Library system ops -- base class
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

__all__ = ['LibraryBase',
           ]

from gingerprawn.api.webop import automated as auto

class LibraryBase(object):
    def __init__(self, baseurl, cache=None):
        self._baseurl = baseurl
        self._bot = auto.Automator(baseurl)
        self._lastop = '__init__'
        LibraryBase.init_cache(self, cache)

    def __del__(self):
        # update cache before deletion
        self.sync_cache()

    def chk_last_op(self, precede=None, logout_permitted=False):
        if self._lastop == 'logout' and not logout_permitted:
            raise RuntimeError('operation not permitted after logout')

        if precede is not None and self._lastop != precede:
            raise ValueError(
            "logic error! last op should be '%s', actually was '%s'" % (
                    precede, self._lastop, ))

    def init_cache(self, cfgobj):
        self._cache = cfgobj

    def sync_cache(self):
        if self._cache is None:
            # cache not set, silently ignore this fact
            return

        self._cache.writeback()

    def set_user_info(self, *args, **kwargs):
        raise NotImplementedError

    def do_login(self, *args, **kwargs):
        raise NotImplementedError

    def do_logout(self, *args, **kwargs):
        raise NotImplementedError

    def get_basicinfo(self, *args, **kwargs):
        raise NotImplementedError

    def get_book_list(self, *args, **kwargs):
        raise NotImplementedError

    def renew_book(self, *args, **kwargs):
        raise NotImplementedError


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
