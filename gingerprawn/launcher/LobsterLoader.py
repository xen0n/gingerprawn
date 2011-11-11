#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Boa:Frame:LobsterLoader
# gingerprawn / launcher / loader frame
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


import sys
import threading

# for managing proper termination when under autostart circumstances
import Queue

# for lengthened splash window displaying
import time
sleep = time.sleep

import wx

# dummy i18n
_ = lambda x: x

from gingerprawn.api import logger
from gingerprawn.api.utils.security import is_valid_modulename

# Eventually I must use the inspect functionality to automatically
# insert logging callback functions into the globals namespace
# to save the team's PRECIOUS free time -- 15:05, 2011-03-30
# 16:06: i have done this -- see below
logger.install()

# prepare to load all the shrimp
from gingerprawn import VERSION_STR
import gingerprawn.api.cooker
cooker = gingerprawn.api.cooker

# univlib initialization postponed
# it's now in initthread.

# Now we're in pkg toplevel, remember that!
# NOTE: the launcher's directory got renamed just before transition to DVCS..
SPLASH_IMG = './launcher/splash.png'

# The "meta-shrimp" that implements the main UI.
# MODIFIED: moved out to main.py, now this name is in self.options

def create(parent):
    return LobsterLoader(parent)

[wxID_LOBSTERLOADER, wxID_LOBSTERLOADERLBLINDICATOR, wxID_LOBSTERLOADERPBR,
] = [wx.NewId() for _init_ctrls in range(3)]

class LobsterLoader(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_LOBSTERLOADER, name='', parent=prnt,
              pos=wx.Point(443, 191), size=wx.Size(416, 338),
              style=wx.CLIP_CHILDREN | wx.FRAME_NO_TASKBAR | wx.NO_BORDER | wx.FRAME_SHAPED,
              title=u'lobsterloader')
        self.SetClientSize(wx.Size(400, 300))
        self.Center(wx.BOTH)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetCursor(wx.STANDARD_CURSOR)
        self.SetThemeEnabled(True)
        self.SetBackgroundColour(wx.Colour(255, 161, 0))

        self.lblIndicator = wx.StaticText(id=wxID_LOBSTERLOADERLBLINDICATOR,
              label=u'<GingerPrawn>', name=u'lblIndicator', parent=self,
              pos=wx.Point(82, 272), size=wx.Size(87, 14), style=0)
        self.lblIndicator.SetToolTipString(u'')
        self.lblIndicator.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.pbr = wx.Gauge(id=wxID_LOBSTERLOADERPBR, name=u'pbr', parent=self,
              pos=wx.Point(383, 2), range=100, size=wx.Size(15, 295),
              style=wx.GA_VERTICAL)

    def __init__(self, parent):
        logdebug('Loader frame init')

        self._init_ctrls(parent)
        if not _APP_OPTIONS.autostart:
            self.splash_init()
        else:
            # only "bringup" needed
            self.BringupFrame()

    def splash_init(self):
        logdebug('Configuring splash screen')

        # first fix version display
        svn_idx = VERSION_STR.find(u' SVN-')
        ver_label = VERSION_STR if svn_idx == -1 \
                else VERSION_STR.replace('SVN-', 'r')
        self.lblIndicator.SetLabel(ver_label)
        # set up splash image
        logdebug('Setting up splash image')
        bmp = self.bmap = wx.Bitmap(SPLASH_IMG)
        self.w = bmp.GetWidth()
        self.h = bmp.GetHeight()
        self.d = bmp.GetDepth()

        self.rgnBG = wx.RegionFromBitmap(bmp)
        del bmp

        popupSizeX, popupSizeY = self.bmap.GetSize()
        self.viewableSize = (popupSizeX, popupSizeY, )
        self.SetClientSize(self.viewableSize)

        # Exactly center the completed popup window in the screen.
        screenSizeX, screenSizeY = wx.DisplaySize()
        popupPosn = ((screenSizeX-popupSizeX)/2, (screenSizeY-popupSizeY)/2)
        self.SetPosition(popupPosn)

        self.Show(True)       # Just for GTK's wx.EVT_WINDOW_CREATE
        self.Show(False)      # Avoid an annoying white window flash
        self.BringupFrame()

        self.Bind(wx.EVT_PAINT, self.OnPaint) # Just calls DrawShapedWindow()

        if wx.Platform == "__WXGTK__":
            # wxGTK requires that the window be created before you can set
            # its shape, so delay the call to SetWindowTransparencies until
            # this event.
            # This event just calls SetWindowTransparencies()
            self.Bind(wx.EVT_WINDOW_CREATE, self.BringupFrame)

    def BringupFrame(self):
        logdebug('Bringing up loader frame')

        is_autostart = _APP_OPTIONS.autostart

        if not is_autostart:
            self.SetWindowShape()
            seq_lock = threading.Lock()
            # added showfirst lock to prevent race condition when two threads
            # start execution. This will keep the init thread from functioning
            # until gradualshow thread has finished.
            showfirst_lock = threading.Lock()
            showfirst_lock.acquire()

            wx.CallAfter(self.spawn_initthread, seq_lock, showfirst_lock)
            wx.CallAfter(self.spawn_GradualShow, seq_lock, showfirst_lock)
        else:
            logdebug('Started along with OS, taking shortcut')
            # no need to show frame
            self.Hide()
            wx.CallAfter(self.spawn_initthread, autostart=True)

    def spawn_GradualShow(self, seq_lock, showfirst_lock):
        def _gradualshow_thread(self,
                totaltime=0.45, granularity=64, targetalpha=0.8):
            seq_lock.acquire()
            tgt = targetalpha * 255.0 # to ensure float
            delta = tgt / granularity
            val = 0.0
            dt = float(totaltime) / granularity
            for i in range(granularity):
                val += delta
                wx.CallAfter(self.SetTransparent, int(val))
                sleep(dt)
            seq_lock.release()
            showfirst_lock.release()

        logdebug('Spawning GradualShow_Thread')
        th = threading.Thread(target=_gradualshow_thread,
                args=(self, ), name='GradualShow_Thread')
        th.setDaemon(True)
        th.start()

    def SetWindowShape(self):
        self.SetShape(self.rgnBG)

    def OnPaint(self, event):
        self.DrawShapedWindow()
        event.Skip()             # Required for using a wx.ClientDC

    def DrawShapedWindow(self):
        if wx.Platform == '__WXGTK__':
            dc = wx.GCDC(wx.ClientDC(self))
        else :
            dc = wx.ClientDC(self)        # This is OK for MSW
        dc.DrawBitmap(self.bmap, 0, 0, True)

    def ProgressCallback(self, status, shrimp, percentage=None):
        if status == 'fail':
            wx.CallAfter(wx.MessageBox, "Shrimp '%s' load failed!" % shrimp,
                    'gingerprawn loader', wx.ICON_WARNING)

        if percentage is not None:
            wx.CallAfter(self.pbr.SetValue, percentage)
        wx.CallAfter(self.lblIndicator.SetLabel, shrimp)

    def LightProgressCallback(self, status, shrimp, percentage=None):
        # used for splashless initialization
        if status == 'fail':
            wx.CallAfter(wx.MessageBox, "Shrimp '%s' load failed!" % shrimp,
                    'gingerprawn loader', wx.YES | wx.ICON_WARNING)


    def spawn_initthread(self, seq_lock=None, showfirst_lock=None,
            autostart=False):
        def init_threadproc(self):
            if not autostart:
                showfirst_lock.acquire()
                showfirst_lock.release()

                seq_lock.acquire()
            else:
                self.Hide()

            # moved from module level to this place to (significantly)
            # improve user experience
            # NOTE: univlib's init MUST come before all shrimp's init,
            # because some of the shrimp (like academic) depend on
            # univlib.current at module level, thus univlib must be available
            # when they're being loaded.
            if not autostart:
                wx.CallAfter(self.lblIndicator.SetLabel, _(u'加载大学支持库'))

            # init univlib ahead of time
            from gingerprawn.api import univlib
            # FIXED: not hardcoded anymore, can be changed via cmdline
            # default value moved there
            univlib.set_current_univ(_APP_OPTIONS.univ_sel)

            logdebug('Attempt to load all shrimp')

            # explicit discovery of shrimp, as close to the loading part as
            # possible
            cooker.do_discovery()

            if not autostart:
                cooker.load_shrimp(self.ProgressCallback)
            else:
                # auto-start, be silent
                cooker.load_shrimp(self.LightProgressCallback)

            if not autostart:
                wx.CallAfter(self.pbr.SetValue, 100)
                wx.CallAfter(self.lblIndicator.SetLabel, _(u'主界面初始化'))

            if autostart:
                # auto start alongside OS bootup, no main interface.
                # Instead ask all shrimp to display their startup interface
                # such as a reminder
                num_shrimp = len(cooker.SHRIMP_MODULES)
                queue = Queue.Queue(num_shrimp)

                # it's quite OK to directly execute this init code in
                # the same thread
                cooker.do_autostart(queue)

                # wait for all shrimp to finish, this is cooperative
                for i in range(num_shrimp):
                    # simply get one signal indicating who has finished
                    exit_shrimp = queue.get(block=True)
                    logdebug('shrimp `%s\' announced exit', exit_shrimp)

                logdebug('all shrimp exited, bailing out')
                wx.CallAfter(self.Destroy)
                return
            else:
                # name of main module is now present at self.options.mainmod
                MAIN_MODULE = _APP_OPTIONS.mainmod
                logdebug('Initializing metashrimp %s', MAIN_MODULE)
                # this name needs checking for sake of security
                if not is_valid_modulename(MAIN_MODULE):
                    logcritical('Metashrimp name invalid')
                    wx.CallAfter(wx.MessageBox, 'Invalid module name!',
                            'gingerprawn', wx.ICON_ERROR)
                    wx.CallAfter(self.Destroy)
                    seq_lock.release()
                    return

                main_stat = cooker.SHRIMP_LOADSTATUS.get(MAIN_MODULE, 'fail')
                if main_stat == 'fail':
                    logcritical('Metashrimp loading failed')
                    wx.CallAfter(wx.MessageBox, 'Main module load failed!',
                            'gingerprawn', wx.ICON_ERROR)
                    wx.CallAfter(self.Destroy)
                    seq_lock.release()
                    return

                try:
                    logdebug('Attempt to bring up metashrimp')
                    cooker.bring_up_shrimp(MAIN_MODULE) # (self.app, ))
                except (ValueError, KeyError, ):
                    logcritical('Metashrimp loading success but bringup failed')
                    wx.CallAfter(wx.MessageBox, 'Failed to bring up main UI!',
                            'gingerprawn', wx.ICON_ERROR)
                    wx.CallAfter(self.Destroy)
                finally:
                    seq_lock.release()
                    logdebug('initthread normal exit')
                    return

        logdebug('Spawning init thread')
        initthread = threading.Thread(target=init_threadproc,
                args=(self, ), name='GingerPrawn_InitThread')
        initthread.setDaemon(True)
        initthread.start()


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
