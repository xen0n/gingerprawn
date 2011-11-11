#!/usr/bin/env python
# -*- coding: utf-8 -*-
# JNMaster / lobster / shrimp entry point, main frontend
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
    'name':   u'江大侠',
    'ver':    u'0.1.0',
    'author': [
               u'\u738b\u96ea\u745e@\u6570\u5a92\u5b66\u9662 (xenon@JNRain)',
               u'\u5c0fC@\u6570\u5a92\u5b66\u9662 (TheC@JNRain)',
               u'\u848b\u9a04\u5929@\u7269\u8054\u7f51\u9662 (JLT@JNRain)',
               ],
    'desc':   u'\u6c5f\u5927\u4fa0\u2014\u2014\u751f\u6d3b\u5c3d\u5728\u6307'
              u'\u5c16\uff0c\u6c5f\u5927\u4eba\u81ea\u5df1\u7684\u6821\u56ed'
              u'\u751f\u6d3b\u5ba2\u6237\u7aef',
    'copyr':  u'(C) 2011 \u6c5f\u5927\u4fa0\u5f00\u53d1\u56e2\u961f',
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

# maybe a better icon will be designed
from lobster_icon import SHRIMP_ICON

################################################################
## SHRIMP DESCRIPTION END, GLOBAL DECLARATIONS AND SHRIMP PROCS
################################################################

import sys
import os

import wx

from gingerprawn import VERSION_STR
from gingerprawn.api.utils.metaprogramming import fun2meth

from gingerprawn.api import cooker
from gingerprawn.api.cooker import iconmgr
from gingerprawn.api import univlib

from gingerprawn.api import logger
logger.install()

from gingerprawn.api.platform import w32version

# dummy placeholder for i18n
_ = lambda x: x

def shrimp_init():
    logdebug('lobster init routine')
    pass

_SELF_FRAME = None
_SHRIMP_ARGS = None

def shrimp_threadproc(args):
    global _SHRIMP_ARGS
    _SHRIMP_ARGS = args
    reason = args[0]

    if reason == 'autostart':
        # starting with OS, do nothing
        waitqueue = args[1]

        # If all shrimp behave well, it's impossible to block here
        # Simply put something to indicate that we're done.
        waitqueue.put('lobster')

        return

    # GUI init should take place in the main thread
    wx.CallAfter(_APP_OBJECT._On_LobsterInit, create)

def shrimp_down(just_querying=False):
    if just_querying:
        ret = wx.MessageBox(_(u'真的要退出吗？'), _(u'\u6c5f\u5927\u4fa0'),
                wx.YES_NO | wx.ICON_QUESTION)
        if ret == wx.YES:
            logdebug('shutdown request approved')
            return True
        else:
            logdebug('shutdown request declined')
            return False

    # not kidding, we have to go now
    loginfo('lobster teardown initiated')
    wx.CallAfter(_SELF_FRAME.Destroy)

#############################################################################
## SEPARATOR BETWEEN SHRIMP ARCHITECTURE AND (MAINLY) GUI IMPLEMENTATION
#############################################################################

# (rather) cool UI when using Windows with Aero enabled~
from gingerprawn.api.platform import aero
# 2 icons belonging to lobster itself
from lobster_icon import SETTINGS_ICON, LOBSTER_ABOUT_ICON
# aboutbox factored out as a common utility
from gingerprawn.api.ui.aboutbox import show_aboutbox
# settings dialog, almost barebone
from lobster_setting_dlg import invoke_dlg as show_settings

SHRIMPBTN_NAME_FMT = 'BtnShrimp%d'
SHRIMPBTN_EVTBUTTON_FMT = 'On%sButton' % SHRIMPBTN_NAME_FMT
SHRIMPBTN_ID_FMT = 'wxID_LOBSTER_MAINBTNSHRIMP%d'
# now this is dynamically calculated, but leave this as an initial reference
SHRIMPBTN_INITIAL_NUM_PER_ROW = 4

SHRIMPBTN_HGAP = 10
SHRIMPBTN_VGAP = 10
SHRIMPBTN_SIZETUPLE = (iconmgr.ICON_WIDTH + 16, iconmgr.ICON_HEIGHT + 16)

## FIXED: WINDOWSIZE_PAD gets calculated EVERY TIME the window is sized,
## AND this time it's derived automatically from system metrics, so
## this is more robust against theme changes and OS variations.
#class WindowSizePadProvider(object):
#    @staticmethod
#    def GetPadX():
#        return wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_X) * 2
#    @staticmethod
#    def GetPadY():
#        return (wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_Y) * 2 +
#                wx.SystemSettings.GetMetric(wx.SYS_CAPTION_Y))
#    @staticmethod
#    def __getitem__(idx):
#        if idx == 0:
#            fn = WindowSizePadProvider.GetPadX
#        elif idx == 1:
#            fn = WindowSizePadProvider.GetPadY
#        else:
#            raise IndexError('the requested dimension does not exist')
#        return fn()
#
#WINDOWSIZE_PAD = WindowSizePadProvider()

def create(parent):
    global _SELF_FRAME
    _SELF_FRAME = lobster_main(parent)
    return _SELF_FRAME

[wxID_LOBSTER_MAIN, wxID_LOBSTER_MAINBTNABOUT, wxID_LOBSTER_MAINBTNSETTING,
        wxID_LOBSTER_MAINBTNBOARD, ] = [wx.NewId() for _init_ctrls in range(4)]

class lobster_main(wx.Frame):
    def _calc_width(self, num_col):
        return ((SHRIMPBTN_SIZETUPLE[0] + SHRIMPBTN_HGAP) * num_col
                - SHRIMPBTN_HGAP) # + WINDOWSIZE_PAD[0])

    def _calc_height(self, num_row):
        return ((SHRIMPBTN_SIZETUPLE[1] + SHRIMPBTN_VGAP) * num_row
                - SHRIMPBTN_VGAP) # + WINDOWSIZE_PAD[1])

    def _calc_size(self):
        num_row = self._ShrimpButtonRowCount
        num_col = len(self._ShrimpButtonCols)
        return wx.Size(self._calc_width(num_col), self._calc_height(num_row))

    def _init_sizers(self):
        self.bag = wx.GridBagSizer(hgap=SHRIMPBTN_HGAP, vgap=SHRIMPBTN_VGAP)
        self.bag.SetEmptyCellSize(wx.Size(*SHRIMPBTN_SIZETUPLE))

        self.DoLayout(self.bag, True) # is_initial=True

        self.btnboard.SetSizer(self.bag)
        self.btnboard.SetAutoLayout(True)

    def DoLayout(self, sizer, is_initial=False):
        sizer.Clear()
        if is_initial:
            num_per_row = SHRIMPBTN_INITIAL_NUM_PER_ROW
        else:
            num_per_row = self.GetSize()[0] / (SHRIMPBTN_SIZETUPLE[0] +
                    sizer.GetHGap())
            if num_per_row == 0:
                num_per_row = 1

        # Got bitten by the nasty shallowcopy thing!!
        # must manually add each of the empty lists here -- a lesson learnt
        self._ShrimpButtonCols = btn_arr = [[] for i in range(num_per_row)]

        # first put those shrimp buttons into the sizer
        # MODIFIED: insert settings button as well (a nasty kludge)
        # this var is named "left" because the about button is at the right...
        # how silly... who can come up with a better name?
        left_buttons = self._ShrimpButtons[:]
        left_buttons.append(self.btnSetting)
        for idx, btn in enumerate(left_buttons):
            row, col = divmod(idx, num_per_row)
            sizer.AddWindow(btn, (row, col),
                    border=0, flag=0, span=(1, 1))
            btn_arr[col].append(btn)

        # ... then the (somewhat lonely) about button
        # now it won't be lonely any more since i decided to put it back
        # along with those cute shrimp buttons
        # (right-justify though)
        aboutbtn_row_idx, rem = divmod(len(left_buttons), num_per_row)
        sizer.AddWindow(self.btnAbout, (aboutbtn_row_idx, num_per_row - 1),
                border=0, flag=0, span=(1, 1))
        btn_arr[-1].append(self.btnAbout)

        # don't know whether this is needed, but added anyway
        sizer.Layout()
        self._ShrimpButtonRowCount = aboutbtn_row_idx + 1

        newsize = self._calc_size()

        self.__DoNotRedoLayout = True
        # self.SetSize(newsize)
        # This mighty method... eliminated all those pads...
        self.SetClientSize(newsize)
        self.__DoNotRedoLayout = False

    def _init_ctrls(self, prnt):
        wx.Frame.__init__(self, id=wxID_LOBSTER_MAIN, name=u'lobster_main',
              parent=prnt, style=wx.DEFAULT_FRAME_STYLE,
              title=_(u'\u6c5f\u5927\u4fa0 %s') % VERSION_STR)
        self.SetToolTipString(u'')
        self.Center(wx.BOTH)
        self.SetHelpText(u'')

        if wx.Platform == '__WXMSW__':
            self.SetBackgroundColour(wx.SystemSettings.GetColour(
                    wx.SYS_COLOUR_GRADIENTACTIVECAPTION))

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # this is not a "scroller" any more
        self.btnboard = wx.Panel(self, wxID_LOBSTER_MAINBTNBOARD,
                style=wx.TAB_TRAVERSAL, name='btnboard')
        if wx.Platform == '__WXGTK__':
            # not sure if this is the proper colour, but at least on Ubuntu's
            # default theme this looks the same as titlebar's fill color
            self.btnboard.SetBackgroundColour(wx.SystemSettings.GetColour(
                     wx.SYS_COLOUR_CAPTIONTEXT))

        # my icon...
        self.btnSetting = wx.BitmapButton(self.btnboard,
                wxID_LOBSTER_MAINBTNSETTING, SETTINGS_ICON.GetBitmap(),
                (0, 0), SHRIMPBTN_SIZETUPLE, name=u'btnSetting')
        self.btnSetting.SetHelpText(u'')
        self.btnSetting.SetToolTipString(_(u'选项'))
        self.btnSetting.Bind(wx.EVT_BUTTON, self.OnBtnSettingButton,
              id=wxID_LOBSTER_MAINBTNSETTING)

        # my icon...
        self.btnAbout = wx.BitmapButton(self.btnboard,
                wxID_LOBSTER_MAINBTNABOUT, LOBSTER_ABOUT_ICON.GetBitmap(),
                (0, 0), SHRIMPBTN_SIZETUPLE, name=u'btnAbout')
        self.btnAbout.SetHelpText(u'')
        self.btnAbout.SetToolTipString(_(u'\u5173\u4e8e...'))
        self.btnAbout.Bind(wx.EVT_BUTTON, self.OnBtnAboutButton,
              id=wxID_LOBSTER_MAINBTNABOUT)

    def __init__(self, parent):
        logdebug('Lobster frame init')
        self._init_ctrls(parent)

        self.InitShrimpList()
        self._init_sizers()
        self.bag.Layout()

        # now for the crazy full glass effect in Windows~
        if wx.Platform == '__WXMSW__':
            aero.make_full_glass(self)

    def AddShrimpBtn(self, prnt, idx, shrimp):
        btn_name = SHRIMPBTN_NAME_FMT % idx
        id_name = SHRIMPBTN_ID_FMT % idx
        handler_name = SHRIMPBTN_EVTBUTTON_FMT % idx

        # 1st we make a EVT_BUTTON handler which fires up the corresponding
        # shrimp.
        # the method is adapted from the former OnLvwShrimpListItemActivated
        # handler, adding some cool dynamic stuff
        def _FireUpShrimp(self, event):
            try:
                cooker.bring_up_shrimp(shrimp)
            except ValueError:
                # already running
                wx.MessageBox('error: already running!')
            event.Skip()
        _FireUpShrimp.func_name = handler_name
        fun2meth(_FireUpShrimp, self) # , handler_name)

        # Some identifying info...
        icon_bmap = iconmgr.get_bitmap(shrimp)
        name = cooker.get_name(shrimp)

        # Prepare the button...
        newid = self.__dict__[id_name] = wx.NewId()
        tmp = wx.BitmapButton(prnt, newid, icon_bmap, (0, 0),
                SHRIMPBTN_SIZETUPLE) # , style=SHRIMPBTN_STYLE)
        tmp.SetToolTipString(name)
        self.__dict__[btn_name] = tmp
        tmp.Bind(wx.EVT_BUTTON, getattr(self, handler_name), id=newid)

        # set up layout later, so we are basically done here
        # store some lookup information
        self._ShrimpButtons.append(tmp)

    def InitShrimpList(self):
        ldstat = cooker.SHRIMP_LOADSTATUS
        ok_shrimp = [sh for sh in ldstat
                if ldstat[sh] == 'ok' and sh != 'lobster'] # exclude myself
        ok_shrimp.sort()

        appender = self.AddShrimpBtn
        self._ShrimpButtons = []
        parent = self.btnboard
        for idx, sh in enumerate(ok_shrimp):
            appender(parent, idx, sh)

    def OnClose(self, evt):
        loginfo('window close event, initiating shutdown')
        ok_to_shutdown = cooker.query_shutdown()
        if ok_to_shutdown:
            cooker.do_shutdown()
            evt.Skip()
        else:
            evt.Veto() # VETO the wx shutdown!

    def OnBtnAboutButton(self, evt):
        show_aboutbox('lobster', self)

    def OnBtnSettingButton(self, evt):
        # TODO
        show_settings(self)

    def OnSize(self, evt):
        # After some experiments, I found out that self.Size already changed
        # when this event fires.
        # So directly calling the rearrangement routine should cause little to
        # no problem.
        if not self.__DoNotRedoLayout:
            # do it
            self.DoLayout(self.bag)
        evt.Skip()

# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
