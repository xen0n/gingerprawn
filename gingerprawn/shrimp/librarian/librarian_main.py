#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Boa:Frame:librarian_main
# JNMaster / librarian / shrimp entry point, login and main UI
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

SHRIMP_MINVER = (0, 1, 0, )
SHRIMP_PLATFORM = ('all', )
SHRIMP_INFO = {
    # One-key library
    'name':   u'\u4e00\u952e\u56fe\u4e66\u9986',
    'ver':    '0.1.0',
    'author': [u'xenon',
               ],
    'desc':   u'神马时候，能够把整个图书馆搬到我的桌面？',
    'copyr':  u'© 2011 Wang Xuerui',
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

from librarian_icon import SHRIMP_ICON

################################################################
## SHRIMP DESCRIPTION END, GLOBAL DECLARATIONS AND SHRIMP PROCS
################################################################

import wx
from gingerprawn.api import cooker

from gingerprawn.api import logger
logger.install()

from gingerprawn.api import conf
cfg = conf.get_conf()

from gingerprawn.api.utils.security import obfuscate_ob64 as obf
from gingerprawn.api.utils.security import clarify_ob64 as deobf

# i18n placeholder
_ = lambda x: x

_SHRIMP_ARGS = None
__SELF_FRAME = None

def shrimp_init():
    logdebug('librarian init routine')
    pass

def shrimp_threadproc(args):
    global _SHRIMP_ARGS
    _SHRIMP_ARGS = args
    reason = args[0]

    if reason == 'autostart':
        # starting with OS, do nothing
        waitqueue = args[1]

        # If all shrimp behave well, it's impossible to block here
        # Simply put something to indicate that we're done.
        waitqueue.put('librarian')

        return

    # GUI init should take place in the main thread
    wx.CallAfter(_APP_OBJECT._On_ShrimpInit, create)

def shrimp_down(just_querying=False):
    if just_querying:
        ret = wx.MessageBox('r u sure?', 'librarian', wx.YES_NO)
        if ret == wx.YES:
            logdebug('shutdown request approved')
            return True
        else:
            logdebug('shutdown request declined')
            return False

    # not kidding, we have to go now
    loginfo('teardown initiated, remembering login info')

    # postprocess login info for writeback
    userinfo = __SELF_FRAME._userinfo
    usr = obf(userinfo['usr'])
    psw = obf(userinfo['psw'])
    # TODO: convert the type too, to prevent possible name change in the future
    typ = userinfo['typ']

    cfg.ensure_section('userid')
    cfg.set('userid', 'u', usr)
    cfg.set('userid', 'p', psw)
    cfg.set('userid', 't', typ)
    cfg.writeback()

    # work done, leave
    wx.CallAfter(__SELF_FRAME.Destroy)

def create(parent):
    global __SELF_FRAME
    __SELF_FRAME = librarian_main(parent)
    return __SELF_FRAME

#############################################################################
## SEPARATOR BETWEEN SHRIMP ARCHITECTURE AND (MAINLY) GUI IMPLEMENTATION
#############################################################################

# from gingerprawn.api.platform import aero
from gingerprawn.api.ui.aboutbox import show_aboutbox

import librarian_userinfo_dlg as userinfo_dlg

[wxID_LIBRARIAN_MAIN, wxID_LIBRARIAN_MAINBTNABOUT,
 wxID_LIBRARIAN_MAINBTNAUTORENEW, wxID_LIBRARIAN_MAINBTNBOOKLIST,
 wxID_LIBRARIAN_MAINBTNEXIT, wxID_LIBRARIAN_MAINBTNSETINFO,
 wxID_LIBRARIAN_MAINPANEL1,
] = [wx.NewId() for _init_ctrls in range(7)]

class librarian_main(wx.Frame):
    def _init_coll_mainsizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.btnSetInfo, (0, 0), border=0, flag=wx.EXPAND,
              span=(1, 1))
        parent.AddWindow(self.btnAbout, (0, 1), border=0, flag=wx.EXPAND,
              span=(1, 1))
        parent.AddWindow(self.btnExit, (0, 2), border=0, flag=wx.EXPAND,
              span=(1, 1))
        parent.AddWindow(self.btnBookList, (1, 0), border=0, flag=wx.EXPAND,
              span=(1, 1))
        parent.AddWindow(self.btnAutoRenew, (1, 1), border=0, flag=wx.EXPAND,
              span=(1, 1))

    def _init_coll_mainsizer_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableRow(0)
        parent.AddGrowableRow(1)
        parent.AddGrowableCol(0)
        parent.AddGrowableCol(1)

    def _init_sizers(self):
        # generated method, don't edit
        self.mainsizer = wx.GridBagSizer(hgap=10, vgap=10)

        self._init_coll_mainsizer_Items(self.mainsizer)
        self._init_coll_mainsizer_Growables(self.mainsizer)

        self.panel1.SetSizer(self.mainsizer)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_LIBRARIAN_MAIN, name='', parent=prnt,
              pos=wx.Point(447, 275), size=wx.Size(288, 111),
              style=wx.DEFAULT_FRAME_STYLE, title=u'librarian')
        self.SetClientSize(wx.Size(272, 73))
        self.Bind(wx.EVT_CLOSE, self.OnLibrarian_mainClose)

        self.panel1 = wx.Panel(id=wxID_LIBRARIAN_MAINPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), style=wx.TAB_TRAVERSAL)

        self.btnExit = wx.Button(id=wxID_LIBRARIAN_MAINBTNEXIT,
              label=_(u'\u9000\u51fa'), name=u'btnExit', parent=self.panel1,
              pos=wx.Point(196, 0), size=wx.Size(75, 32), style=0)
        self.btnExit.Bind(wx.EVT_BUTTON, self.OnBtnExitButton,
              id=wxID_LIBRARIAN_MAINBTNEXIT)

        self.btnSetInfo = wx.Button(id=wxID_LIBRARIAN_MAINBTNSETINFO,
              label=_(u'\u8bbe\u7f6e\u767b\u5f55\u4fe1\u606f'),
              name=u'btnSetInfo', parent=self.panel1, pos=wx.Point(0, 0),
              size=wx.Size(97, 32), style=0)
        self.btnSetInfo.Bind(wx.EVT_BUTTON, self.OnBtnSetInfoButton,
              id=wxID_LIBRARIAN_MAINBTNSETINFO)

        self.btnAbout = wx.Button(id=wxID_LIBRARIAN_MAINBTNABOUT,
              label=_(u'\u5173\u4e8e'), name=u'btnAbout', parent=self.panel1,
              pos=wx.Point(107, 0), size=wx.Size(79, 32), style=0)
        self.btnAbout.Bind(wx.EVT_BUTTON, self.OnBtnAboutButton,
              id=wxID_LIBRARIAN_MAINBTNABOUT)

        self.btnBookList = wx.Button(id=wxID_LIBRARIAN_MAINBTNBOOKLIST,
              label=_(u'\u5f53\u524d\u501f\u9605\u5217\u8868'),
              name=u'btnBookList', parent=self.panel1, pos=wx.Point(0, 42),
              size=wx.Size(97, 30), style=0)
        self.btnBookList.Bind(wx.EVT_BUTTON, self.OnBtnBookListButton,
              id=wxID_LIBRARIAN_MAINBTNBOOKLIST)

        self.btnAutoRenew = wx.Button(id=wxID_LIBRARIAN_MAINBTNAUTORENEW,
              label=u'\u4e00\u952e\u7eed\u501f', name=u'btnAutoRenew',
              parent=self.panel1, pos=wx.Point(107, 42), size=wx.Size(79, 30),
              style=0)
        self.btnAutoRenew.Bind(wx.EVT_BUTTON, self.OnBtnAutoRenewButton,
              id=wxID_LIBRARIAN_MAINBTNAUTORENEW)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)
        # don't call Fit() here, or the frame becomes VERY small
        self.SetMinSize(self.GetSize())
        # aero.make_full_glass(self)

        # fill the login info structure
        self._userinfo = {'usr': deobf(cfg.get('userid', 'u', u'')),
                'psw': deobf(cfg.get('userid', 'p', u'')),
                'typ': cfg.get('userid', 't', ''),
                }

    def OnLibrarian_mainClose(self, event):
        loginfo('window close event, initiating subshrimp shutdown')
        ok_to_shutdown = cooker.query_shutdown('librarian')
        if ok_to_shutdown:
            cooker.bring_down_shrimp('librarian')
            event.Skip()
        else:
            event.Veto() # VETO the wx shutdown!

    def OnBtnExitButton(self, event):
        self.Close()

    def OnBtnSetInfoButton(self, event):
        dummydest = self._userinfo
        userinfo_dlg.invoke_dlg(self, self._userinfo)
        # DEBUG
        wx.MessageBox(u'用户名 %s, 密码 %s, 登陆类型 %s' % (dummydest['usr'],
                dummydest['psw'],
                `dummydest['typ']`,
                ))

    def OnBtnAboutButton(self, event):
        show_aboutbox('librarian', self)

    def OnBtnBookListButton(self, event):
        event.Skip()

    def OnBtnAutoRenewButton(self, event):
        event.Skip()


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
