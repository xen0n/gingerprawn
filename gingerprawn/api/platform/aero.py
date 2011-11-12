#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.platform / support for Aero Glass under Windows
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

'''\
This module provides support for utilizing Aero Glass translucency
effect on Windows 7, designed to work with wxPython.

On other platforms which do not support DWM, the module's all functions
become dummy.
'''

import sys
import ctypes

# quick check. now only 32- and 64-bit machines are common
INT_SIZE = 4 if sys.maxint == 0x7fffffff else 8

# the message sent when composition state changes
WM_DWMCOMPOSITIONCHANGED = 0x031E

# the real MARGINS structure, no more simulating and kludge...
class MARGINS(ctypes.Structure):
    '''\
    ``ctypes`` wrapper for the underlying C structure ``MARGINS``\ .
    '''
    _fields_ = [('left', ctypes.c_int),
                ('right', ctypes.c_int),
                ('top', ctypes.c_int),
                ('bottom', ctypes.c_int),
                ]

from gingerprawn.api.utils.metaprogramming import fun2meth

import wx

if sys.platform == 'win32':
    try:
        # Need to see if there actually is DWM.
        _dwmapi = ctypes.windll.dwmapi
        has_dwm = True
    except WindowsError:
        # not present.
        has_dwm = False
else:
    has_dwm = False

# NOTE: For auto-documentation to properly extract the docstrings, we override
# the has_dwm result.
try:
    _APP_OPTIONS._is_autodoc
    # Inside Sphinx, expose the real functions
    has_dwm = True
except AttributeError:
    pass

# Functions.
if has_dwm:
    import wxmsw_wndhook
    def is_composition_enabled():
        '''\
        Returns ``True`` if desktop composition is (supported) and enabled,
        otherwise ``False``\ .
        '''
        buf = ctypes.create_string_buffer(INT_SIZE)
        ret = _dwmapi.DwmIsCompositionEnabled(buf) == 0
        # returning in this way ensures nothing wrong is done when the above
        # function call fails.
        return ret and (buf.value == '\x01')

    def _make_glass(frame, left=-1, right=-1, top=-1, bottom=-1):
        '''\
        Worker function for making the calls to Windows API and setting
        up the appropriate message hook.
        '''
        # prerequisites checking removed now
        # because this function is merely a worker function
        # back up the current bg color
        frame._BackgroundColourBackup = frame.GetBackgroundColour()
        frame.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        hwnd = frame.GetHandle()
        # invoke the API, making a MUCH nicer MARGIN structure
        # NOTE byref is needed to pass pointer, otherwise Windows will try
        # to read from, say, 0xFFFFFFFF.
        ret = _dwmapi.DwmExtendFrameIntoClientArea(hwnd,
                ctypes.byref(MARGINS(left, right, top, bottom)))
        return ret

    def make_glass(frame, left=-1, right=-1, top=-1, bottom=-1):
        '''\
        Make a ``wx.Frame`` object translucent, giving it a full glass
        look by default. This behavior can be overridden by explicitly
        specifying the margin values through the four additional parameters.
        '''
        # the message handler for WM_DWMCOMPOSITIONCHANGED
        def OnDwmCompositionChanged(self, wParam, lParam):
            if is_composition_enabled():
                _make_glass(self, left, right, top, bottom)
            else:
                self.SetBackgroundColour(self._BackgroundColourBackup)
            self.Refresh()
            return True
        fun2meth(OnDwmCompositionChanged, frame)

        # first set up the effect properly
        if is_composition_enabled():
            _make_glass(frame, left, right, top, bottom)

        # hook the WndProc so as to catch WM_DWMCOMPOSITIONCHANGED
        # NOTE here we don't wrap these lines also into that if stmt,
        # because Aero can be disabled when we're started, but enabled
        # later.
        wxmsw_wndhook.install_hooks(frame)
        frame.addMsgHandler(WM_DWMCOMPOSITIONCHANGED,
                frame.OnDwmCompositionChanged)
        frame.hookWndProc()

    def make_full_glass(frame):
        '''\
        This function is mainly here for compatibility.

        It's also a convenient way to make a ``Frame`` fully translucent.
        '''
        # Just a compatibility wrapper now...
        make_glass(frame)

else:
    # platform doesn't have DWM, make some dummy functions
    def is_composition_enabled():
        return False

    def make_glass(frame, left=-1, right=-1, top=-1, bottom=-1):
        return False

    def make_full_glass(frame):
        return False


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
