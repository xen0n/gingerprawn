#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.platform / notification - win32 platform support
# depends on Windows API
# XXX This code is supported only in Windows XP and later versions
# because of the changing data structure
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

# TODO: an __all__ to get rid of all ctypes things leaking into global

from ctypes import *

# our base class
from notifier_base import NotifierBase

#############################################################################

# since we wouldn't consider Windows 9x support, Unicode version is used
# MSDN Library reference is at:
# http://msdn.microsoft.com/en-us/library/bb762159%28v=vs.85%29.aspx
Shell_NotifyIcon = windll.shell32.Shell_NotifyIconW

#
# NOTIFYICONDATA structure.
#
# MSDN Library reference:
# http://msdn.microsoft.com/en-us/library/bb773352%28v=vs.85%29.aspx

# First we need a little union helper...
class _timeout_or_version(Union):
    _fields_ = [
            ('uTimeout', c_uint32),
            ('uVersion', c_uint32),
            ]

# then a GUID structure...
# XXX Is this really needed? Maybe just a 16-byte string without \0 here...
class GUID(Structure):
    _fields_ = [
            ('Data1', c_uint32),
            ('Data2', c_uint16),
            ('Data3', c_uint16),
            ('Data4', c_ubyte * 8),
            ]

# finally the NOTIFYICONDATA
class NOTIFYICONDATA(Structure):
    '''\
    The NOTIFYICONDATA structure used to manipulate system tray icons in
    Windows.
    Original definition:

typedef struct _NOTIFYICONDATAW {
    DWORD cbSize;
    HWND hWnd;
    UINT uID;
    UINT uFlags;
    UINT uCallbackMessage;
    HICON hIcon;
#if (NTDDI_VERSION < NTDDI_WIN2K)
    WCHAR  szTip[64];
#endif
#if (NTDDI_VERSION >= NTDDI_WIN2K)
    WCHAR  szTip[128];
    DWORD dwState;
    DWORD dwStateMask;
    WCHAR  szInfo[256];
    union {
        UINT  uTimeout;
        UINT  uVersion;  // used with NIM_SETVERSION, values 0, 3 and 4
    } DUMMYUNIONNAME;
    WCHAR  szInfoTitle[64];
    DWORD dwInfoFlags;
#endif
#if (NTDDI_VERSION >= NTDDI_WINXP)
    GUID guidItem;
#endif
#if (NTDDI_VERSION >= NTDDI_LONGHORN)
    HICON hBalloonIcon;
#endif
} NOTIFYICONDATAW, *PNOTIFYICONDATAW;

typedef NOTIFYICONDATAW NOTIFYICONDATA;
typedef PNOTIFYICONDATAW PNOTIFYICONDATA;

'''
    _fields_ = [
            ('cbSize', c_uint32),
            ('hWnd', c_uint),
            ('uID', c_uint32),
            ('uFlags', c_uint32),
            ('uCallbackMessage', c_uint32),
            # XXX handles represented as uint's here, are there better ways
            # to describe 'em? /-:
            ('hIcon', c_uint),
            ('szTip', c_wchar * 128),
            ('dwState', c_uint32),
            ('dwStateMask', c_uint32),
            ('szInfo', c_wchar * 256),
            # this is the quirk... must undergo another level of dot...
            # Win32 header calls this DUMMYUNIONNAME, which is #define'd as
            # #define DUMMYUNIONNAME
            ('_time_or_ver', _timeout_or_version),
            ('szInfoTitle', c_wchar * 64),
            ('dwInfoFlags', c_uint32),
            ('guidItem', GUID),
            ('hBalloonIcon', c_uint),
            ]

#
# Supporting constants
#
# well, the #define's are prefixed with a ... well... # sign

[
    NOTIFYICONDATA_V1_SIZE, # for Shell32 DLL version < 5.0
    NOTIFYICONDATA_V2_SIZE, # for Shell32 ver 5.0 (Windows 2000)
    NOTIFYICONDATA_V3_SIZE, # for Shell32 ver 6.0 (Windows XP)
    # For versions higher than 6.0.6 (Vista or later) just use sizeof(...),
    # that'd be 956 as of Windows 7.
    ] = (152, 936, 952, )

#if (_WIN32_IE >= 0x0500)
#define NIN_SELECT          (WM_USER + 0)
#define NINF_KEY            0x1
#define NIN_KEYSELECT       (NIN_SELECT | NINF_KEY)
#endif

#if (_WIN32_IE >= 0x0501)

#define NIN_BALLOONHIDE         (WM_USER + 3)
#define NIN_BALLOONTIMEOUT      (WM_USER + 4)
#define NIN_BALLOONUSERCLICK    (WM_USER + 5)
#endif
#if (NTDDI_VERSION >= NTDDI_LONGHORN)
#define NIN_POPUPOPEN           (WM_USER + 6)
#define NIN_POPUPCLOSE          (WM_USER + 7)
#endif // (NTDDI_VERSION >= NTDDI_LONGHORN)


#define NIM_ADD         0x00000000
#define NIM_MODIFY      0x00000001
#define NIM_DELETE      0x00000002
#if (_WIN32_IE >= 0x0500)
#define NIM_SETFOCUS    0x00000003
#define NIM_SETVERSION  0x00000004
[
    NIM_ADD,
    NIM_MODIFY,
    NIM_DELETE,
    NIM_SETFOCUS,
    NIM_SETVERSION,
    ] = range(5)

## set NOTIFYICONDATA.uVersion with 0, 3 or 4
## please read the documentation on the behavior difference that the
## different versions imply

#define     NOTIFYICON_VERSION      3
#if (NTDDI_VERSION >= NTDDI_LONGHORN)
#define     NOTIFYICON_VERSION_4    4
#endif // (NTDDI_VERSION >= NTDDI_LONGHORN)
#endif

#define NIF_MESSAGE     0x00000001
#define NIF_ICON        0x00000002
#define NIF_TIP         0x00000004
#if (_WIN32_IE >= 0x0500)
#define NIF_STATE       0x00000008
#define NIF_INFO        0x00000010
#endif
#if (_WIN32_IE >= 0x600)
#define NIF_GUID        0x00000020
#endif
#if (NTDDI_VERSION >= NTDDI_LONGHORN)
#define NIF_REALTIME    0x00000040
#define NIF_SHOWTIP     0x00000080
#endif // (NTDDI_VERSION >= NTDDI_LONGHORN)
[
    NIF_MESSAGE,
    NIF_ICON,
    NIF_TIP,
    NIF_STATE,
    NIF_INFO,
    NIF_GUID,
    NIF_REALTIME,
    NIF_SHOWTIP,
    ] = [1 << i for i in range(8)]

#if (_WIN32_IE >= 0x0500)
#define NIS_HIDDEN              0x00000001
#define NIS_SHAREDICON          0x00000002
NIS_HIDDEN, NIS_SHAREDICON = 1, 2

## says this is the source of a shared icon

## Notify Icon Infotip flags
#define NIIF_NONE       0x00000000
## icon flags are mutually exclusive
## and take only the lowest 2 bits
#define NIIF_INFO       0x00000001
#define NIIF_WARNING    0x00000002
#define NIIF_ERROR      0x00000003
#if (NTDDI_VERSION >= NTDDI_XPSP2) // also available in NTDDI_WS03SP1
#define NIIF_USER       0x00000004
[
    NIIF_NONE,
    NIIF_INFO,
    NIIF_WARNING,
    NIIF_ERROR,
    NIIF_USER,
    ] = range(5)

#endif // (NTDDI_VERSION >= NTDDI_XPSP2)
#define NIIF_ICON_MASK  0x0000000F
#if (_WIN32_IE >= 0x0501)
#define NIIF_NOSOUND    0x00000010
#endif
#endif
#if (NTDDI_VERSION >= NTDDI_LONGHORN)
#define NIIF_LARGE_ICON 0x00000020
#endif // (NTDDI_VERSION >= NTDDI_LONGHORN)
NIIF_ICON_MASK, NIIF_NOSOUND, NIIF_LARGE_ICON = 0x0f, 0x10, 0x20

# NOTE: supplied the missing definition of NIIF_RESPECT_QUIET_TIME
NIIF_RESPECT_QUIET_TIME = 0x80

#############################################################################

# TODO: add support for icons

class W32Notifier(NotifierBase):
    def __init__(self, appname, frameobj):
        # for Windows there's no need to init
        NotifierBase.__init__(self, appname, frameobj)

        # no need to store a reference to the frame here,
        # because dynamically changing the icon's owner is just
        # plain impossible in Windows using the hWnd+uID way,
        # you need to unregister the icon anyway, and because we are
        # only implementing a notifier here.
        #
        # although a hWnd value of 0 also works, we limit use of this
        # behavior just for ourselves' sanity. Provide null handle ONLY
        # IF the caller *explicitly* asked for that by passing None.
        if frameobj is None:
            self.hWnd = 0
        else:
            self.hWnd = frameobj.GetHandle()

        # internal counter for allocating uID's
        self.__count = 0
        self.__list = []

    def __del__(self):
        # Deletes all icons the class have created...
        hwnd = self.hWnd
        # command format
        cmds = (NOTIFYICONDATA(hWnd=hwnd, uID=i) for i in self.__list)
        # delete 'em
        [Shell_NotifyIcon(NIM_DELETE, byref(data)) for data in cmds]

    def __do_set_icon(self, filename):
        raise NotImplementedError

    def message(self, title, body, timeout=15):
        idx = self.__count
        cmd = NOTIFYICONDATA(
                cbSize=sizeof(NOTIFYICONDATA), # FIXME
                hWnd=self.hWnd,
                uID=idx,
                uFlags=NIF_INFO | NIF_SHOWTIP,
                szInfo=body,
                szInfoTitle=title,
                dwInfoFlags=NIIF_INFO | NIIF_RESPECT_QUIET_TIME,
                )
        ret = Shell_NotifyIcon(NIM_ADD, byref(cmd))
        if ret == 0:
            # failed to register...
            return False
        # notification successfully emitted
        self.__list.append(idx)
        self.__count += 1
        return True

# setup an alias...
Notifier = W32Notifier

#############################################################################
# Simple test cases.

if __name__ == '__main__':
    print 'sizeof(NOTIFYICONDATA) = %u' % sizeof(NOTIFYICONDATA)


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
