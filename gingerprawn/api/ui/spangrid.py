#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.ui / Grid control supporting rowspan
# this is mainly adopted from wxPython demo

import wx
import wx.grid as gridlib

# from gingerprawn.api.utils.titledtable import RowSpanTitledTable

################################################################

class RowSpanGrid(gridlib.Grid):
    def __init__(self, parent, newid=wx.ID_ANY, tbl=None):
        gridlib.Grid.__init__(self, parent, newid)
        if tbl is not None:
            self.SetTitledTable(tbl)

    def SetTitledTable(self, tbl):
        # row count, col count. this is mistaken easily
        self.CreateGrid(len(tbl.processed), tbl.titlelen)

        setval = self.SetCellValue
        setsiz = self.SetCellSize
        setalign = self.SetCellAlignment
#        setrender = self.SetCellRenderer
#        wraprenderer = gridlib.GridCellAutoWrapStringRenderer()
        for row_idx, tr in enumerate(tbl.processed):
            # make use of row_idx, set row height
#            self.SetRowSize(row_idx, 60)
            for col_idx, td in tr:
                setsiz(row_idx, col_idx, td[1], 1) # rowspan
                setalign(row_idx, col_idx, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
#                setrender(row_idx, col_idx, wraprenderer)
                setval(row_idx, col_idx, td[0]) # text

        titles = tbl.titleline
        for col_idx, title in enumerate(titles):
            self.SetColLabelValue(col_idx, title)
            # making use of the loop, set column width
#            self.SetColSize(col_idx, 100)


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
