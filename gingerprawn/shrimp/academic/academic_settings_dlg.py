#!/usr/bin/env python
# -*- coding: utf-8 -*-
# JNMaster / academic / setting dialog
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

# TODO: This is almost the same as librarian/librarian_userinfo_dlg.py, so
# refactoring is definitely needed!

#from gingerprawn.api import logger
#logger.install()

from datetime import datetime as dt

import wx
import wx.lib.sized_controls as sc
import wx.calendar

# this validator is broken when used with wx.SpinCtrl
# from gingerprawn.api.ui.validators import DigitOnlyValidator

# dummy I18N wrapper
_ = lambda x: x

class SettingsDialog(sc.SizedDialog):
    def __init__(self, parent, cfg_obj, section_name, initial):
        sc.SizedDialog.__init__(self, None, -1, _(u'一键教务系统 - 参数设置'),
                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
                | wx.DIALOG_MODAL)

        # remember the configparser object for later update...
        self.__cfg = cfg_obj
        self.__sect = section_name

        pane = self.GetContentsPane()
        pane.SetSizerType('form')

        # row 1
        wx.StaticText(pane, -1, _(u'参考日选取'))
        self.refDate = wx.calendar.CalendarCtrl(pane, -1, wx.DateTime_Now())
        self.refDate.SetSizerProps(expand=True)

        # row 2
        wx.StaticText(pane, -1, _(u'参考日所在教学周'))
        self.refWeek = wx.SpinCtrl(pane, -1, '')
        self.refWeek.SetRange(1,16)
        # self.refWeek.Validator = DigitOnlyValidator()
        self.refWeek.SetSizerProps(expand=True)
        # This control's change event is wx.EVT_SPINCTRL, but we don't need
        # to catch and process it because the data is only gathered when
        # the dialog closes.
        # The same applies to all settings dialogs written in this fashion.

        # row 3
        wx.StaticText(pane, -1, _(u'明日课程自动提醒'))

        # here's how to add a 'nested sizer' using sized_controls
        radioPane = sc.SizedPanel(pane, -1)
        radioPane.SetSizerType('horizontal')
        radioPane.SetSizerProps(expand=True)


        # make these children of the radioPane to have them use
        # the horizontal layout
        self.autoremindSel = {}
        self.autoremindSel[True] = wx.RadioButton(radioPane, -1, _(u'开启'))
        self.autoremindSel[False] = wx.RadioButton(radioPane, -1, _(u'关闭'))
        # end row 3

        # add dialog buttons
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

        # Set initial values
        # this method takes datetime.date{,time}, and that is really nice
        self.refDate.PySetDate(initial['refdate'])
        self.refWeek.SetValue(initial['refweek'])
        self.autoremindSel[initial['is_enabled']].SetValue(True)

    def update_settings(self):
        # this is a datetime.date object!! yummy!!
        new_refdate = self.refDate.PyGetDate()
        # this is an int, not a string, and that's great!
        new_refweek = self.refWeek.GetValue()
        if self.autoremindSel[True].GetValue():
            new_autoremind = True
        elif self.autoremindSel[False].GetValue():
            new_autoremind = False
        else:
            raise ValueError('should never happen!')

        cfg = self.__cfg
        section_name = self.__sect
        cfg.ensure_section(section_name)
        cfg.set_obj(section_name, 'refdate', new_refdate)
        cfg.set(section_name, 'refweek', str(new_refweek))
        cfg.set(section_name, 'enabled', 'yes' if new_autoremind else 'no')
        cfg.writeback()

        return


def invoke_dlg(prnt, cfg_obj, section_name, initial):
    # use the previous data to initialize the form
    dlg = SettingsDialog(prnt, cfg_obj, section_name, initial)
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
