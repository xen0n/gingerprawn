#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.ui / customized status bar
# taken from wxPython demo
# TODO: generalize this... get things done

import wx

class ProgressStatusBar(wx.StatusBar):
    def __init__(self, parent,
            field_proportion=[2, 1],
            interval=40,
            start_pulse=False):
        wx.StatusBar.__init__(self, parent, -1)

        self.SetFieldsCount(len(field_proportion))
        # Sets the fields to be relative widths to each other.
        self.SetStatusWidths([-i for i in field_proportion])

        self.sizeChanged = False
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # Field 0 ... just text
        self.SetStatusText(u'', 0)

        self.interval = interval

        # This will fall into field 1 (the second field)
        self.pbr = wx.Gauge(self, 1001)
        # set pbr to pulsing mode
        self.pbr.Pulse()

        # set the initial position of the progress bar
        self.Reposition()

        # We're going to use a timer to drive the pulsing progress bar.
        self.timer = wx.PyTimer(self.DoPulse)
        if start_pulse:
            self.timer.Start(interval)
            self.is_pulsing = True
        else:
            self.pbr.Hide()
            self.is_pulsing = False

    # status toggler
    def ToggleStatus(self, start=None):
        if start is None:
            self.ToggleStatus(not self.is_pulsing)
            return

        if start:
            if not self.is_pulsing:
                self.pbr.Show()
                self.timer.Start(self.interval)
                self.is_pulsing = True
        else:
            if self.is_pulsing:
                self.timer.Stop()
                self.pbr.Hide()
                self.is_pulsing = False

    def DoPulse(self):
        # dare simplify this even further??
        self.pbr.Pulse()

    def OnSize(self, evt):
        self.Reposition()  # for normal size events

        # Set a flag so the idle time handler will also do the repositioning.
        # It is done this way to get around a buglet where GetFieldRect is not
        # accurate during the EVT_SIZE resulting from a frame maximize.
        self.sizeChanged = True

    def OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()

    # reposition the checkbox
    def Reposition(self):
        rect = self.GetFieldRect(1)
        self.pbr.SetPosition((rect.x+2, rect.y+2))
        self.pbr.SetSize((rect.width-4, rect.height-4))
        self.sizeChanged = False

    ############################################################
    ## Provide an interface similar to the plain text-only statusbar...
    def SetStatusText(self, txt, pos=None):
        return wx.StatusBar.SetStatusText(self, txt, 0 if pos is None else pos)


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
