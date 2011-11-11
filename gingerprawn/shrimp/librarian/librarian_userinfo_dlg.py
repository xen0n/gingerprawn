#!/usr/bin/env python
# -*- coding: utf-8 -*-
# JNMaster / librarian / Login info dialog implementation
# XXX This has a good chance of being factored out and becoming a part of
# the gingerprawn framework after some generalizations.
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

import wx
import wx.lib.sized_controls as sc

# dummy I18N wrapper
_ = lambda x: x

# TODO: remove this ugly direct copy ASAP!!!
# this issue is not as serious as a FIXME so downgraded it
LOGINTYPE_CERTNO = 'cert_no'
LOGINTYPE_BARNO = 'bar_no'
LOGINTYPE_EMAIL = 'email'

class UserInfoDialog(sc.SizedDialog):
    def __init__(self, parent, initial):
        sc.SizedDialog.__init__(self, None, -1, _(u'登录信息设定'),
                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
                | wx.DIALOG_MODAL)

        pane = self.GetContentsPane()
        pane.SetSizerType('form')

        # row 1
        wx.StaticText(pane, -1, _(u'帐号'))
        self.usrCtrl = wx.TextCtrl(pane, -1, _(u''))
        self.usrCtrl.SetSizerProps(expand=True)

        # row 2
        wx.StaticText(pane, -1, _(u'密码'))
        self.pswCtrl = wx.TextCtrl(pane, -1, u'',  style=wx.TE_PASSWORD)
        self.pswCtrl.SetSizerProps(expand=True)

        # row 3
        wx.StaticText(pane, -1, _(u'登录类型'))

        # here's how to add a 'nested sizer' using sized_controls
        radioPane = sc.SizedPanel(pane, -1)
        radioPane.SetSizerType('horizontal')
        radioPane.SetSizerProps(expand=True)

        # make these children of the radioPane to have them use
        # the horizontal layout
        self.isStud = wx.RadioButton(radioPane, -1, _(u'学号'))
        self.isCert = wx.RadioButton(radioPane, -1, _(u'借阅证号'))
        self.isMail = wx.RadioButton(radioPane, -1, _(u'电子邮件'))
        # end row 3

        # add dialog buttons
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

        # Set initial values for quick modification
        self.usrCtrl.SetValue(initial['usr'])
        self.pswCtrl.SetValue(initial['psw'])

        _typ = initial['typ']
        if _typ == LOGINTYPE_CERTNO:
            self.isStud.SetValue(True)
        elif _typ == LOGINTYPE_BARNO:
            self.isCert.SetValue(True)
        elif _typ == LOGINTYPE_EMAIL:
            self.isMail.SetValue(True)
        else:
            # should not happen; if really is the case, set to
            # student number.
            self.isStud.SetValue(True)

def invoke_dlg(prnt, dest):
    # use the previous data to initialize the form
    dlg = UserInfoDialog(prnt, dest)
    dlg.CenterOnScreen()

    # this does not return until the dialog is closed.
    val = dlg.ShowModal()

    if val == wx.ID_OK:
        # OK button, dest shall be replaced
        if dlg.isStud.GetValue():
            typ = LOGINTYPE_CERTNO
        elif dlg.isCert.GetValue():
            typ = LOGINTYPE_BARNO
        elif dlg.isMail.GetValue():
            typ = LOGINTYPE_EMAIL
        else:
            # According to the source code, this is very unlikely to happen,
            # unless someone uses a debugging tool to tweak our control's
            # internal state. Treat this as an error.
            raise ValueError('Nothing selected for login type!!')

        # If we get to this point, typ must be set. Directly using it is ok.
        dest['usr'] = dlg.usrCtrl.GetValue()
        dest['psw'] = dlg.pswCtrl.GetValue()
        dest['typ'] = typ
    else:
        # Cancel button, do nothing
        pass

    # This is mandatory, otherwise the app won't terminate when we close down!
    dlg.Destroy()


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
