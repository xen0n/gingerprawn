#!/usr/bin/env python
# -*- coding: utf-8 -*-
# JNMaster / academic / shrimp entry point, login and main UI
# major part by Chen Huayue, later massively refactored by Wang Xuerui
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

SHRIMP_MINVER = (0, 1, 0, )
SHRIMP_PLATFORM = ('all', )
SHRIMP_INFO = {
    # Teaching Affair System
    'name':   u'一键教务系统',
    'ver':    '0.1.0',
    'author': [u'thec@JNRain <489412949@qq.com>',
               u'xenon@JNRain <idontknw.wang@gmail.com>',
               ],
    'desc':   u'更方便的学校教务系统操作；\n'
              u'如果它能给你提供方便那这几行代码就死得瞑目了~',
    'copyr':  u'© 2011 Chen Huayue, Wang Xuerui',
    'lic':    u'''\
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
''',
    }

from academic_icon import SHRIMP_ICON

################################################################
## SHRIMP DESCRIPTION END, GLOBAL DECLARATIONS AND SHRIMP PROCS
################################################################

from datetime import datetime as dt

import wx

from gingerprawn.api import cooker
from gingerprawn.api import logger
logger.install()

from gingerprawn.api import conf
cfg = conf.get_conf()
cfgcache = conf.get_conf('jwxtcache', 'txt')

_USERID_SECT = 'userid'

from gingerprawn.api.utils.security import obfuscate_ob64 as obf
from gingerprawn.api.utils.security import clarify_ob64 as deobf

# i18n placeholder
_ = lambda x: x

_SHRIMP_ARGS = None
__SELF_FRAME = None

def shrimp_init():
    logdebug('academic init routine')
    pass

def shrimp_threadproc(args):
    global _SHRIMP_ARGS
    _SHRIMP_ARGS = args
    reason = args[0]

    if reason == 'autostart':
        # TODO: push sth
        waitqueue = args[1]

        wx.CallAfter(show_autoremind, None, cfg, cfgcache)

        # If all shrimp behave well, it's impossible to block here
        # Simply put something to indicate that we're done.
        waitqueue.put('academic')

        return

    # GUI init should take place in the main thread
    wx.CallAfter(_APP_OBJECT._On_ShrimpInit, create)

def shrimp_down(just_querying=False):
    if just_querying:
        ret = wx.MessageBox(_(u'确定要退出吗？'), _(u'一键教务系统'), wx.YES_NO)
        if ret == wx.YES:
            logdebug('shutdown request approved')
            return True
        else:
            logdebug('shutdown request declined')
            return False

    # not kidding, we have to go now
    loginfo('teardown initiated, remembering username and password')
    usr = obf(__SELF_FRAME.dlN.GetValue())
    psw = obf(__SELF_FRAME.dlP.GetValue())
    cfg.ensure_section(_USERID_SECT)
    cfg.set(_USERID_SECT, 'u', usr)
    cfg.set(_USERID_SECT, 'p', psw)

    cfg.writeback()

    # work done, leave
    wx.CallAfter(__SELF_FRAME.Destroy)

def create(parent):
    global __SELF_FRAME
    __SELF_FRAME = academic_main(parent)
    return __SELF_FRAME

#############################################################################
## SEPARATOR BETWEEN SHRIMP ARCHITECTURE AND (MAINLY) GUI IMPLEMENTATION
#############################################################################

from gingerprawn.api.ui.aboutbox import show_aboutbox

# statusbar class with a pulsing progress bar, very good for showing
# progress
from gingerprawn.api.ui.statusbar import ProgressStatusBar

# nasty nonpackage problem
# TODO: fix relative import in shrimp...
from academic_curricula_frame import invoke as show_curricula_frame
from academic_score_frame import invoke as show_score_frame
from academic_settings_dlg import invoke_dlg as show_settings_dlg
from academic_autoremind import invoke as show_autoremind
from academic_autoremind import get_autoremind_cfg

# Layout constants
WindowSize = (270, 180)

FirstLineSpace = 10
LineHeight = 30 # modified for better look under wxGTK (Ubuntu Linux)
LineIndent = 10

class academic_main(wx.Frame):
    # for layout use
    def GetOrder(self, start=0):
        cur = [start]
        def incr(add, LineAdd=0):
            cur[0] += add
            return wx.Point(LineIndent + LineAdd,
                            FirstLineSpace + LineHeight * cur[0])
        return incr

    def _init_ctrls(self, prnt):
        wx.Frame.__init__(self, prnt, wx.ID_ANY,
                _(u'教务信息查询'), size=WindowSize)
        self.SetMaxSize(WindowSize)
        self.SetMinSize(WindowSize)
        self.SetIcon(wx.IconFromBitmap(SHRIMP_ICON.GetBitmap()))

        # set background color to get some native feel on MSW
        if wx.Platform == '__WXMSW__':
            self.SetBackgroundColour(wx.SystemSettings.GetColour(
                    wx.SYS_COLOUR_3DFACE))

        # MENU
        M=wx.Menu()
        M_Pref = M.Append(wx.ID_PREFERENCES, _(u'设置'), _(u'设置模块的各种参数'))
        M_exit = M.Append(wx.ID_EXIT, _(u'退出'), _(u'关闭本模块'))
        A=wx.Menu()
        A_about = A.Append(wx.ID_ABOUT, _(u'关于'), _(u'关于本模块'))

        MB=wx.MenuBar()
        MB.Append(M, _(u'程序'))
        MB.Append(A, _(u'关于'))
        self.SetMenuBar(MB)

        # LAYOUT
        order=self.GetOrder(0)
        # xenon add: enable tab traversal
        pnl = self.panelMain = wx.Panel(self, wx.ID_ANY, style=wx.EXPAND)

        wx.StaticText(pnl, label=_(u"账号"), pos=order(0))
        self.dlN = wx.TextCtrl(pnl, pos=order(0, 35),
                size=(160, -1))
        self.dlN.SetValue(deobf(cfg.get(_USERID_SECT, 'u', '')))

        wx.StaticText(pnl, label=_(u'密码'), pos=order(1))
        self.dlP = wx.TextCtrl(pnl, pos=order(0, 35), size=(160, -1),
                style=wx.TE_PASSWORD)
        self.dlP.SetValue(deobf(cfg.get(_USERID_SECT, 'p', '')))

        self.btnShowCurricula = wx.Button(pnl, pos=order(1),
                label=_(u"查询个人课表"))
        self.btnShowScores = wx.Button(pnl, pos=order(0, 90),
                label=_(u"查询个人成绩"))

        # xenon add: to make the panel expand to fill the entire frame
        self.box = wx.BoxSizer()
        self.box.AddWindow(pnl)
        self.box.Layout()

        # FUNCTIONS
        self.Bind(wx.EVT_MENU, self.OnMenuPref, M_Pref)
        self.Bind(wx.EVT_MENU, self.OnMenuExit, M_exit)
        self.Bind(wx.EVT_MENU, self.OnMenuAbout, A_about)
        self.Bind(wx.EVT_BUTTON, self.OnKB, self.btnShowCurricula)
        self.Bind(wx.EVT_BUTTON, self.OnCJ, self.btnShowScores)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # STATUS
        self.statusbar = ProgressStatusBar(self)
        self.SetStatusBar(self.statusbar)
        self.SetStatusText(_(u'准备就绪'))
        self.Show(True)

    def __init__(self, prnt):
        self._init_ctrls(prnt)

    def OnClose(self, event):
        loginfo('window close event, initiating subshrimp shutdown')
        ok_to_shutdown = cooker.query_shutdown('academic')
        if ok_to_shutdown:
            cooker.bring_down_shrimp('academic')
            event.Skip()
        else:
            event.Veto() # VETO the wx shutdown!

    def OnMenuAbout(self, evt):
        show_aboutbox('academic', self)

    def OnMenuPref(self, evt):
        show_settings_dlg(self, cfg, 'reminder', get_autoremind_cfg(cfg))

    def OnMenuExit(self, evt):
        self.Close()

    #####################################################

    def get_userinfo(self):
        usr = self.dlN.GetValue()
        psw = self.dlP.GetValue()
        return {'usr': usr, 'psw': psw, }

    def OnKB(self, evt):
        show_curricula_frame(self, self.get_userinfo(), cfgcache)
        # evt.Skip()

    def OnCJ(self, evt):
        # DONE: well... showing a grid-based thing is OK
        show_score_frame(self, self.get_userinfo(), cfgcache)

    def notify_status(self, msg):
        self.SetStatusText(msg)

    def toggle_working(self):
        self.statusbar.ToggleStatus()


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
