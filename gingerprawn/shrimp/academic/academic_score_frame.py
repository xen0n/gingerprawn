#!/usr/bin/env python
# -*- coding: utf-8 -*-
# JNMaster / academic / score querier
# by Chen Huayue, then mostly rewritten by Wang Xuerui
#
# Copyright (C) 2011 Chen Huayue <489412949@qq.com>
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

import threading

import wx

# dummy i18n
_ = lambda x: x

from gingerprawn.api import logger
logger.install()

# (really) cool Grid control
from gingerprawn.api.ui.dragablegrid import DragableGrid

# university academic affairs system's interface
from gingerprawn.api import univlib
jwxt = univlib.current.jwxt

# for common login behavior
from academic_login_mixin import JWXTLoginThreadMixin

#############################################################################
## SEPARATOR BETWEEN DECLARATIONS AND (MAINLY) GUI IMPLEMENTATION
#############################################################################

WINDOW_SIZE = (900, 300)

class score_frame(wx.Frame, JWXTLoginThreadMixin):
    def _init_ctrls(self):
        self.scoregrid = DragableGrid(self)

    def _init_grid(self, grid, tbl):
        grid.SetTable(tbl)
        # auto size, thanks to Robin Dunn for pointing out the method in an
        # earlier post in the wx mailing list, resulted in a MUCH BETTER look
        grid.AutoSize()
        self.Fit()

    # the name is a bit misleading, but is consistent with login behavior...
    def _LoginThread(self, prnt, userinfo, cfg_obj):
        # Call the common login routine thru the mixin...
        JWXTLoginThreadMixin._LoginThread(self, prnt, userinfo, cfg_obj)

        wx.CallAfter(prnt.notify_status, _(u'准备查询成绩'))
        if not self._affairs.prepare4scores():
            wx.CallAfter(prnt.notify_status, _(u'页面打开失败，请稍后再试>_<'))
            wx.CallAfter(prnt.toggle_working)
            wx.CallAfter(self.Destroy)
            return

        wx.CallAfter(prnt.notify_status, _(u'查询中'))
        if not self._affairs.get_scores():
            wx.CallAfter(prnt.notify_status, _(u'成绩查询失败，请稍后再试- -'))
            wx.CallAfter(prnt.toggle_working)
            wx.CallAfter(self.Destroy)
            return

        # the score table is at our disposal (=
        tbl = self._affairs.scores
        wx.CallAfter(self._init_grid, self.scoregrid, tbl)

        # Show method invoked before logout, so that result appears more
        # timely, enhancing user experience.
        wx.CallAfter(self.Show)

        # Call LogoutThread code...
        # That piece of code is already meant to be executed in a separate
        # thread, so directly invoking is perfectly OK.
        # self pointer and parent window
        JWXTLoginThreadMixin._LogoutThread(self, prnt, toggle=False) # evt=None

        # The LogoutThread doesn't change the current progressbar visibility
        # (we suppressed its toggling behavior), so we must turn off it manually
        wx.CallAfter(prnt.toggle_working)
        return

    def __init__(self, prnt, userinfo, cfg_obj):
        wx.Frame.__init__(self, prnt, wx.ID_ANY, title=_(u'成绩单'),
                size=WINDOW_SIZE)

        self.__parent = prnt
        self._init_ctrls()

        # Evt bindings.
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        ########################################################
        ## INITIALIZATION
        thrd = threading.Thread(target=self._LoginThread,
                args=(prnt, userinfo, cfg_obj, ),
                name='academic_ScoreThread')
        thrd.daemon = True
        thrd.start()

    def OnClose(self, evt):
        self.__parent.notify_status(_(u'成绩窗体已关闭'))
        self.Destroy()
        evt.Skip()

def invoke(prnt, userinfo, cfg_obj):
    frame = score_frame(prnt, userinfo, cfg_obj)
    # frame.Show()


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
