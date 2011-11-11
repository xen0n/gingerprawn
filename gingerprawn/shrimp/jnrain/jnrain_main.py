#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Boa:Frame:jnrain_main
# JNMaster / jnrain / shrimp entry point, main UI
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

# TODO: haven't done any work yet!!!

import wx

from gingerprawn.api import logger
logger.install()

from gingerprawn.api import cooker

# i18n placeholder
_ = lambda x: x

SHRIMP_MINVER = (0, 1, 0, )
SHRIMP_PLATFORM = ('all', )
SHRIMP_INFO = {
    # One-key JNRain
    'name':   u'\u4e00\u952e\u542c\u96e8',
    'ver':    '0.1.0',
    'author': ['xenon',
               ],
    'desc':   '<desc here>',
    'copyr':  u'(C) 2011 Wang Xuerui',
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

from jnrain_icon import SHRIMP_ICON

_SHRIMP_ARGS = None
__SELF_FRAME = None

def shrimp_init():
    logdebug('jnrain init routine')
    pass

def shrimp_threadproc(args):
    global _SHRIMP_ARGS
    _SHRIMP_ARGS = args
    reason = args[0]

    if reason == 'autostart':
        # TODO: push Top10 posts
        waitqueue = args[1]

        wx.CallAfter(wx.MessageBox, 'DO SOMETHING!', 'JNRain')

        # If all shrimp behave well, it's impossible to block here
        # Simply put something to indicate that we're done.
        waitqueue.put('jnrain')

        return

    # GUI init should take place in the main thread
    wx.CallAfter(_APP_OBJECT._On_ShrimpInit, create)

def shrimp_down(just_querying=False):
    if just_querying:
        ret = wx.MessageBox('r u sure?', 'jnrain', wx.YES_NO)
        if ret == wx.YES:
            logdebug('shutdown request approved')
            return True
        else:
            logdebug('shutdown request declined')
            return False

    # not kidding, we have to go now
    loginfo('teardown initiated')
    wx.CallAfter(__SELF_FRAME.Destroy)

def create(parent):
    global __SELF_FRAME
    __SELF_FRAME = jnrain_main(parent)
    return __SELF_FRAME

[wxID_JNRAIN_MAIN, wxID_JNRAIN_MAINBTNEXIT,
] = [wx.NewId() for _init_ctrls in range(2)]

class jnrain_main(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_JNRAIN_MAIN, name='', parent=prnt,
              pos=wx.Point(500, 107), size=wx.Size(400, 400),
              style=wx.DEFAULT_FRAME_STYLE, title=u'jnrain')
        self.SetClientSize(wx.Size(384, 362))
        self.Bind(wx.EVT_CLOSE, self.OnJnrain_mainClose)

        self.btnExit = wx.Button(id=wxID_JNRAIN_MAINBTNEXIT,
              label=_(u'\u9000\u51fa'), name=u'btnExit', parent=self,
              pos=wx.Point(120, 16), size=wx.Size(75, 24), style=0)
        self.btnExit.Bind(wx.EVT_BUTTON, self.OnBtnExitButton,
              id=wxID_JNRAIN_MAINBTNEXIT)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnJnrain_mainClose(self, event):
        loginfo('window close event, initiating subshrimp shutdown')
        ok_to_shutdown = cooker.query_shutdown('jnrain')
        if ok_to_shutdown:
            cooker.bring_down_shrimp('jnrain')
            event.Skip()
        else:
            event.Veto() # VETO the wx shutdown!

    def OnBtnExitButton(self, event):
        self.Close()
        event.Skip()


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
