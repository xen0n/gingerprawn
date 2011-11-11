#!/usr/bin/env python
# -*- coding: utf-8 -*-
# JNMaster / academic / curriculum querier interface
# the original code was contributed by Chen Huayue, later almost entirely
# rewritten by Wang Xuerui.
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
# import wx.html

# dummy i18n
_ = lambda x: x

from gingerprawn.api import logger
logger.install()

# university academic affairs system's interface
from gingerprawn.api import univlib
jwxt = univlib.current.jwxt

# for common login behavior
from academic_login_mixin import JWXTLoginThreadMixin

#############################################################################
## SEPARATOR BETWEEN DECLARATIONS AND (MAINLY) GUI IMPLEMENTATION
#############################################################################

# statusbar class with a pulsing progress bar, very good for showing
# progress
from gingerprawn.api.ui.statusbar import ProgressStatusBar

# for an (again) very fancy curriculum page
from gingerprawn.api.ui.spangrid import RowSpanGrid

# Layout constants
KBSize=(300, 160)
showKBSize=(1280, 768)

FirstLineSpace = 10
LineHeight = 30 # modified for better look under wxGTK (Ubuntu Linux)
LineIndent = 10

class curricula_frame(wx.Frame, JWXTLoginThreadMixin):
    # for layout use
    def GetOrder(self, start=0):
        cur = [start]
        def incr(add, LineAdd=0):
            cur[0] += add
            return wx.Point(LineIndent + LineAdd,
                            FirstLineSpace + LineHeight * cur[0])
        return incr

    def _LoginThread(self, parent, userinfo, cfg_cache):
        JWXTLoginThreadMixin._LoginThread(self, parent, userinfo, cfg_cache)

        wx.CallAfter(parent.notify_status, _(u'获取学年与学期信息'))
        self._kbList1, self._kbList2 = self._affairs.prepare4curriculum()
        yr_default, tm_default = self._affairs.curriculum_defaults
        yr_default = self._kbList1.index(yr_default)
        tm_default = self._kbList2.index(tm_default)

        # List of choice initialization postponed, because the lists
        # are not yet available at the time of overall frame init
        wx.CallAfter(self.kbL1.SetItems, self._kbList1)
        wx.CallAfter(self.kbL2.SetItems, self._kbList2)
        wx.CallAfter(self.kbL2.InvalidateBestSize)
        wx.CallAfter(self.kbL1.Fit)
        wx.CallAfter(self.kbL2.Fit)

        wx.CallAfter(self.kbL1.Select, yr_default)
        wx.CallAfter(self.kbL2.Select, tm_default)

        wx.CallAfter(self.SetStatusText, _(u'请选择学年和学期'))

        wx.CallAfter(parent.notify_status, _(u'准备就绪'))
        wx.CallAfter(parent.toggle_working)

        wx.CallAfter(self.Show)
        return

    def __init__(self, parent, userinfo, cfg_cache):
        wx.Frame.__init__(self, parent, wx.ID_ANY, _(u'课表查询'), size=KBSize)
        self.SetMaxSize(KBSize)
        self.SetMinSize(KBSize)
        self.__parent = parent
        # bind the close handler to auto-logout before closing down
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # set background color to get some native feel on MSW
        if wx.Platform == '__WXMSW__':
            self.SetBackgroundColour(wx.SystemSettings.GetColour(
                    wx.SYS_COLOUR_3DFACE))

        # this is preserved for the showing frame
        self.__userid = userinfo['usr']

        ########################################################
        ## LAYOUT SPEC
        order=self.GetOrder(0)
        pnl = self.panelMain = wx.Panel(self, wx.ID_ANY, style=wx.EXPAND)
        wx.StaticText(pnl, wx.ID_ANY, _(u'课表查询'), pos=order(0))
        self.kbL1 = wx.Choice(pnl, pos=order(1), size=(130, -1))
        self.kbL2 = wx.Choice(pnl, pos=order(0, 135), size=(60, -1))

        self.kbB=wx.Button(pnl, label=_(u'查询'), pos=order(0, 204),
                           size=(60, -1))
        wx.StaticText(pnl, label=_(u'请从下拉菜单中选择想查询的学期'),
                      pos=order(1))

        self.Bind(wx.EVT_BUTTON, self.KB, self.kbB)

        self.statusbar = ProgressStatusBar(self)
        self.SetStatusBar(self.statusbar)

        ########################################################
        ## INITIALIZATION
        thrd = threading.Thread(target=self._LoginThread,
                args=(parent, userinfo, cfg_cache, ),
                name='academic_LoginThread')
        thrd.daemon = True
        thrd.start()

    def OnClose(self, evt):
        thrd = threading.Thread(target=self._LogoutThread,
                args=(self.__parent, ), # toggle=True
                name='academic_LogoutThread')
        thrd.daemon = True
        thrd.start()
        evt.Skip()

    def _QueryThread(self, yr, tm):
        wx.CallAfter(self.notify_status, _(u'查询中'))
        wx.CallAfter(self.toggle_working)

        try:
            self._affairs.get_curriculum(yr, tm) #, raw=True)
        except Exception, e:
            logexception('unexpected exc:\n%s', `e`)
            wx.CallAfter(self.notify_status,
                         _(u'查询出错，请重试；若仍然出错，请报告 Bug'))
            wx.CallAfter(self.toggle_working)
            return

        _r = self._affairs.curriculum[(yr, tm)]
        # gui operation must be protected
        wx.CallAfter(self.do_showKB, _r)
        wx.CallAfter(self.toggle_working)
        return

    def KB(self, evt):
        # Gather and validate input.
        yr = self._affairs.curriculum_years[self.kbL1.GetSelection()]
        if yr == -1:
            self.SetStatusText(_(u'学年不能为空'))
            return
        term = self._affairs.curriculum_terms[self.kbL2.GetSelection()]

        # Data gathering complete, spawn worker thread.
        thrd = threading.Thread(target=self._QueryThread,
                args=(yr, term, ),
                name='academic_QueryThread')
        thrd.daemon = True
        thrd.start()

    def do_showKB(self, rawdata):
        '''\
        This GUI operation must be done in the main thread, so we have to
        encapsulate it into a function.
        '''
        showKB(self, rawdata, self.__userid)

    def notify_status(self, msg):
        self.SetStatusText(msg)

    def toggle_working(self):
        self.statusbar.ToggleStatus()

class showKB(wx.Frame):
    def __init__(self, parent, content, username):
        wx.Frame.__init__(self, parent,
                title=_(u'%s 的课表') % username,
                size=showKBSize)

        self.__parent = parent
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        try:
            self.curriculum_grid = RowSpanGrid(self, wx.ID_ANY, content)
        except:
            logexception('exc when opening grid window for result')
            parent.SetStatusText(
                    _(u'无法展开课表，请重试；若仍然失败，请报告 Bug'))

        # this auto size, thanks to Robin Dunn for pointing out the method in an
        # earlier mail list post, has brought a MUCH BETTER look
        self.curriculum_grid.AutoSize()
        self.Fit()

        # we're done, show up!
        self.Show(True)
        parent.notify_status(_(u'课表已打开'))

#        html = wx.html.HtmlWindow(self)
#        if wx.Platform == '__WXGTK__':
#            html.SetStandardFonts()
#        try:
#            html.SetPage(content)
#            self.Show(True)
#            parent.notify_status(_(u'课表已打开'))
#        except:
#            logexception('exc when opening htmlwindow for result')
#            parent.SetStatusText(
#                    _(u'无法展开课表，请重试；若仍然失败，请报告 Bug'))

    def OnClose(self, evt):
        self.__parent.notify_status(_(u'课表窗口已关闭'))
        evt.Skip()

def invoke(prnt, userinfo, cfg_obj):
    frame = curricula_frame(prnt, userinfo, cfg_obj)
    # frame.Show()


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
