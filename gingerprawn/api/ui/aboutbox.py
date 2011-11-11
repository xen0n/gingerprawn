#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.ui / easier-to-use aboutbox wrapping
# code mainly borrowed from wxPython demo code for AboutDialog

import wx
from wx.lib.wordwrap import wordwrap

#----------------------------------------------------------------------
# update: fetch the REAL info, instead of duplicating
from gingerprawn.api import cooker as ckr

def show_aboutbox(shrimp, frame):
    # First we create and fill the info object
    info = wx.AboutDialogInfo()
    info.Name = ckr.get_name(shrimp)
    info.Version = ckr.get_version(shrimp)
    info.Copyright = ckr.get_copyright(shrimp)
    info.Description = wordwrap(ckr.get_desc(shrimp), 350, wx.ClientDC(frame))
    # TODO: MUST REPLACE THIS HARDCODED URL WITH REAL VALUE!
    info.WebSite = ('http://bbs.jnrain.com', u'\u6c5f\u5357\u542c\u96e8')
    info.Developers = ckr.get_authors(shrimp)
    info.License = wordwrap(ckr.get_license(shrimp), 400, wx.ClientDC(frame))

    # Then we call wx.AboutBox giving it that info object
    wx.AboutBox(info)


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
