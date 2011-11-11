#!/usr/bin/env python
# -*- coding: utf-8 -*-
# JNMaster / academic / common login behavior factored out as mixin
# Copyright (C) 2011 Wang Xuerui <idontknw.wang@gmail.com>
# contains code Copyright (C) 2011 Chen Huayue <489412949@qq.com>
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

import wx

# dummy i18n
_ = lambda x: x

from gingerprawn.api import logger
logger.install()

# university academic affairs system's interface
from gingerprawn.api import univlib
jwxt = univlib.current.jwxt

class JWXTLoginThreadMixin(object):
    def _LoginThread(self, parent, userinfo, cfg_cache):
        wx.CallAfter(parent.notify_status, _(u'登陆系统中'))
        wx.CallAfter(parent.toggle_working)

        self._affairs = jwxt.JiangnanAcademicAffairs()

        # Init cache.
        self._affairs.init_cache(cfg_cache)

        self._affairs.set_user_info(userinfo['usr'], userinfo['psw'])
        try:
            self._affairs.do_login()
        except ValueError:
            wx.CallAfter(wx.MessageBox,
                         _(u'用户名或密码错误！请修改后再次查询'), _(u'登录失败'),
                          wx.ICON_ERROR)
            wx.CallAfter(parent.notify_status,
                         _(u'登陆系统失败，请检查用户名与密码'))

            wx.CallAfter(parent.toggle_working)
            wx.CallAfter(self.Destroy)
            return
        except RuntimeError:
            logexception("RuntimeError caught during login")
            if self._affairs.error_reason == 'network':
                # Network error...
                wx.CallAfter(wx.MessageBox,
                             _(u'网络错误，请检查内网是否可以正常访问。。。'),
                              _(u'登录失败'), wx.ICON_ERROR)
                wx.CallAfter(parent.notify_status,
                             _(u'登陆系统失败，请确保内网畅通'))
            else:
                # Other (mysterious) reason...
                wx.CallAfter(wx.MessageBox,
                             _(u'发生运行时错误！请稍后重试。。'),
                             _(u'登录失败'), wx.ICON_ERROR)
                wx.CallAfter(parent.notify_status,
                             _(u'登陆系统失败，请稍后再试'))

            wx.CallAfter(parent.toggle_working)
            wx.CallAfter(self.Destroy)
            return

    def _LogoutThread(self, parent, toggle=True):
        wx.CallAfter(parent.notify_status, _(u'登出系统'))
        if toggle:
            wx.CallAfter(parent.toggle_working)

        try:
            ret = self._affairs.do_logout()
            assert ret == True
            wx.CallAfter(parent.notify_status, _(u'已安全登出'))
        except:
            wx.CallAfter(parent.notify_status, _(u'登出失败，忽略错误'))
            logexception('exc raised when logging out, ignoring')
            pass

        if toggle:
            wx.CallAfter(parent.toggle_working)

        # no need to close the caller window here, the event handler can do
        # the close by itself. this thread is running background and we don't
        # depend on the caller window's data structure, so it's OK here not
        # to pass around the wx.EVT_CLOSE event.
        return


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
