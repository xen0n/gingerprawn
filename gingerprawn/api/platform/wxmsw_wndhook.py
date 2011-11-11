#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.platform / WndProc hook written for working with wxMSW
#
# Copyright (C) 2011 Wang Xuerui <idontknw.wang@gmail.com>
#
## This file is again based on Chris Mellon's WndProcMixinCtypes published on
## the wxPyWiki, removing the mixin wrapper so as to make things easier when
## the frame class is not designed to be aware of platform difference, hence
## not inherited from the mixin.
## Chris Mellon's original description of the WndProcMixinCtypes is preseved;
## see below.
##########################################################################
##
##  This is a modification of the original WndProcHookMixin by Kevin Moore,
##  modified to use ctypes only instead of pywin32, so it can be used
##  with no additional dependencies in Python 2.5
##
##########################################################################
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

import ctypes
from ctypes import c_long, c_int

from gingerprawn.api.utils.metaprogramming import fun2meth

import wx

# Flag to enable message loop debugging
__MSGDEBUG = False

## It's probably not neccesary to make this distinction, but it never hurts
## to be safe
if 'unicode' in wx.PlatformInfo:
    SetWindowLong = ctypes.windll.user32.SetWindowLongW
    CallWindowProc = ctypes.windll.user32.CallWindowProcW
else:
    SetWindowLong = ctypes.windll.user32.SetWindowLongA
    CallWindowProc = ctypes.windll.user32.CallWindowProcA

if __MSGDEBUG:
    from .w32msgs import W32MSG_DICT_WM as __W32MSG
    __getmsgname = __W32MSG.get

# TODO: you can generalize this... maybe.
GWL_WNDPROC = -4
WM_DESTROY  = 2

## Create a type that will be used to cast a python callable to a c callback
## function
## first arg is return type, the rest are the arguments
WndProcType = ctypes.WINFUNCTYPE(c_int, c_long, c_int, c_int, c_int)

def hookWndProc(self):
    self.__localWndProcWrapped = WndProcType(self.localWndProc)
    self.__oldWndProc = SetWindowLong(self.GetHandle(),
                                    GWL_WNDPROC,
                                    self.__localWndProcWrapped)
def unhookWndProc(self):
    SetWindowLong(self.GetHandle(),
                    GWL_WNDPROC,
                    self.__oldWndProc)

    ## Allow the ctypes wrapper to be garbage collected
    self.__localWndProcWrapped = None

def addMsgHandler(self,messageNumber,handler):
    self.__msgDict[messageNumber] = handler

if __MSGDEBUG:
    # debug the message loop... that means printing ALL the messages out.
    # because speed REALLY matters, i made 2 copies of code, then choose one
    # based on the pre-set value __MSGDEBUG.
    def localWndProc(self, hWnd, msg, wParam, lParam):
        # call the handler if one exists
        # performance note: has_key is the fastest way to check for a key
        # when the key is unlikely to be found
        # (which is the case here, since most messages will not have handlers).
        # This is called via a ctypes shim for every single windows message
        # so dispatch speed is important

        # add: debugging code
        print 'MSG: %s (wParam:0x%08X lParam:0x%08X)' % (
                __getmsgname(msg, hex(msg)),
                wParam,
                lParam,
                )

        # actually this is faster than has_key because bindings are gone
        if msg in self.__msgDict:
            # if the handler returns false, we terminate the message here
            # Note that we don't pass the hwnd or the message along
            # Handlers should be really, really careful about returning false
            # here
            if self.__msgDict[msg](wParam,lParam) == False:
                return

        # Restore the old WndProc on Destroy.
        if msg == WM_DESTROY:
            self.unhookWndProc()

        return CallWindowProc(self.__oldWndProc, hWnd, msg, wParam, lParam)
else:
    def localWndProc(self, hWnd, msg, wParam, lParam):
        # call the handler if one exists
        # performance note: has_key is the fastest way to check for a key
        # when the key is unlikely to be found
        # (which is the case here, since most messages will not have handlers).
        # This is called via a ctypes shim for every single windows message
        # so dispatch speed is important

        # UPDATE: we now have the operator "in", which functions exactly like
        # has_key() but requires no runtime binding...
        if msg in self.__msgDict:
            # if the handler returns false, we terminate the message here
            # Note that we don't pass the hwnd or the message along
            # Handlers should be really, really careful about returning false
            # here
            if self.__msgDict[msg](wParam,lParam) == False:
                return

        # Restore the old WndProc on Destroy.
        if msg == WM_DESTROY:
            self.unhookWndProc()

        return CallWindowProc(self.__oldWndProc, hWnd, msg, wParam, lParam)

def install_hooks(obj):
    def create_private_vars(self):
        # replace the ctor
        self.__msgDict = {}
        self.__localWndProcWrapped = None
    fun2meth(create_private_vars, obj)
    fun2meth(hookWndProc, obj)
    fun2meth(unhookWndProc, obj)
    fun2meth(addMsgHandler, obj)
    fun2meth(localWndProc, obj)

    # set up private vars, as if called by a ctor
    obj.create_private_vars()
    del obj.create_private_vars


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
