#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.univlib.backends / BBS Operations -- base class
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

class BBSBase(object):
    def __init__(self, url):
        self._baseurl = url

    def set_user_info(self, usr, psw):
        self.__usr = usr
        self.__psw = psw

    def do_login(self, *args, **kwargs):
        raise NotImplementedError

    def do_logout(self, *args, **kwargs):
        raise NotImplementedError

    def list_boards(self, *args, **kwargs):
        raise NotImplementedError

    def list_posts(self, *args, **kwargs):
        raise NotImplementedError

    def get_top10(self, *args, **kwargs):
        raise NotImplementedError

    def get_bless(self, *args, **kwargs):
        raise NotImplementedError

    def post_topic(self, *args, **kwargs):
        raise NotImplementedError

    def post_reply(self, *args, **kwargs):
        raise NotImplementedError

    def delete_post(self, *args, **kwargs):
        raise NotImplementedError

    def do_admin_work(self, *args, **kwargs):
        raise NotImplementedError


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
