#!/usr/bin/env python
# -*- coding: utf-8 -*-
# JNMaster / lobster / setting dialog
# TODO: This is almost the same as librarian/librarian_userinfo_dlg.py, so
# refactoring is definitely needed!
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

from sys import platform
from gingerprawn.api.platform import autostart

from gingerprawn.api import logger
logger.install()

import wx
import wx.lib.sized_controls as sc

# dummy I18N wrapper
_ = lambda x: x

class SettingsDialog(sc.SizedDialog):
    def __init__(self, parent):
        sc.SizedDialog.__init__(self, None, -1, _(u'江大侠设置'),
                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
                | wx.DIALOG_MODAL)

        pane = self.GetContentsPane()
        pane.SetSizerType('form')

        # row 1
        wx.StaticText(pane, -1, _(u'开机自启动'))

        # here's how to add a 'nested sizer' using sized_controls
        radioPane = sc.SizedPanel(pane, -1)
        radioPane.SetSizerType('horizontal')
        radioPane.SetSizerProps(expand=True)

        # make these children of the radioPane to have them use
        # the horizontal layout
        self.autostartSel = {}
        self.autostartSel[True] = wx.RadioButton(radioPane, -1, _(u'启用'))
        self.autostartSel[False] = wx.RadioButton(radioPane, -1, _(u'关闭'))
        # end row 1

        # add dialog buttons
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

        # Set initial values
        self.__autostart_status = autostart.query_autostart_status()
        self.autostartSel[self.__autostart_status].SetValue(True)

    def update_settings(self):
        if self.autostartSel[self.__autostart_status].GetValue():
            # nothing changed...
            # but we do the modification anyway to ensure consistency
            # in situations where the actual setting gets modified while
            # this dialog is open, and the option, although unchanged,
            # is really meant to be written back
            newstat = self.__autostart_status
        else:
            # autostart status must have changed...
            newstat = not self.__autostart_status

        try:
            autostart.set_autostart_status(newstat)
        except OSError, e:
            logexception('OSError raised when setting autostart status')
            if platform == 'win32' and e.winerror == 5:
                # Access denied, may be blocked by antivirus software.
                # Give a clear notice.
                wx.MessageBox(
                        _(u'没有足够权限进行新状态设置，请检查是否被杀软或防火墙拦截。'),
                        _(u'更新设置异常'),
                        wx.OK | wx.ICON_WARNING)
            else:
                if sys.platform == 'win32':
                    prompt = (_(u'设置过程中发生未知解决方案的 Windows 错误 %d，'
                            u'设置失败')
                            % e.winerror)
                else:
                    prompt = (_(u'设置过程中发生未知解决方案的操作系统错误 %d，'
                            u'设置失败')
                            % e.errno)
                wx.MessageBox(prompt, _(u'更新设置异常'), wx.OK | wx.ICON_ERROR)
        except Exception, e:
            logexception('non-OSError raised when setting autostart status')
            wx.MessageBox(
                    _(u'设置过程中发生未预见的异常 %s，设置失败，请报告 Bug') % `e`,
                    _(u'更新设置异常'),
                    wx.OK | wx.ICON_ERROR)


def invoke_dlg(prnt):
    # use the previous data to initialize the form
    dlg = SettingsDialog(prnt)
    dlg.CenterOnScreen()

    # this does not return until the dialog is closed.
    val = dlg.ShowModal()

    if val == wx.ID_OK:
        dlg.update_settings()
    else:
        # Cancel button, do nothing
        pass

    # This is mandatory, otherwise the app won't terminate!
    dlg.Destroy()


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
