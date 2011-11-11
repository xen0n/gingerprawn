#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.ui / validators
# these are useful for restricting what can be entered into a control.
# these codes are again adopted from the wxPython demo.
# FIXME: These are BROKEN when used together with wx.SpinCtrl...

from string import letters, digits
import wx

class DigitOnlyValidator(wx.PyValidator):
    def __init__(self, flag=None, pyVar=None):
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return DigitOnlyValidator(self.flag)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()

        for x in val:
            if x not in digits:
                return False

        return True


    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in digits:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling event.Skip eats the event before it
        # gets to the text control
        return

class AlphaOnlyValidator(wx.PyValidator):
    def __init__(self, flag=None, pyVar=None):
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return AlphaOnlyValidator(self.flag)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()

        for x in val:
            if x not in letters:
                return False

        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in letters:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling event.Skip eats the event before it
        # gets to the text control
        return


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
