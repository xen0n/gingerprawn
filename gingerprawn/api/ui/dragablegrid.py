#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.ui / draggable Grid control
# this code is taken from wxPython demo with minor modifications

import wx
import wx.grid as gridlib
import wx.lib.gridmovers as gridmovers


from gingerprawn.api.utils.titledtable import TitledTable

#---------------------------------------------------------------------------
class CustomDataTable(gridlib.PyGridTableBase):
    '''\
    usage is basically
    self.SetIdentifiers(['id','ds','sv','pr','pl','op','fx','ts'])
    self.SetRowLabels(['Row1','Row2','Row3'])
    self.SetColLabels({'id':'ID','ds':'Description','sv':'Severity',
                      'pr':'Priority','pl':'Platform','op':'Opened?',
                      'fx':'Fixed?','ts':'Tested?'})
    self.SetData([{'id':1010,
                  'ds':"The foo doesn't bar",
                  'sv':"major",
                  'pr':1,
                  'pl':'MSW',
                  'op':1,
                  'fx':1,
                  'ts':1
                  },
                 {'id':1011,
                  'ds':"I've got a wicket in my wocket",
                  'sv':"wish list",
                  'pr':2,
                  'pl':'other',
                  'op':0,
                  'fx':0,
                  'ts':0
                  },
                 {'id':1012,
                  'ds':"Rectangle() returns a triangle",
                  'sv':"critical",
                  'pr':5,
                  'pl':'all',
                  'op':0,
                  'fx':0,
                  'ts':0
                  }
                 ])
    '''
    def __init__(self):
        gridlib.PyGridTableBase.__init__(self)

        # dummy data
        self.identifiers = []
        self.data = []
        self.colLabels = {}
        self.rowLabels = []

    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.identifiers)

    def IsEmptyCell(self, row, col):
        id = self.identifiers[col]
        return not self.data[row][id]

    def GetValue(self, row, col):
        id = self.identifiers[col]
        return self.data[row][id]

    def SetValue(self, row, col, value):
        id = self.identifiers[col]
        self.data[row][id] = value

    #--------------------------------------------------
    # Some optional methods
    # Called when the grid needs to display column labels
    def GetColLabelValue(self, col):
        id = self.identifiers[col]
        return self.colLabels[id]

    # Called when the grid needs to display row labels
    # MODIFIED: give off 1-based seq numbers when custom
    # values aren't supplied
    def GetRowLabelValue(self,row):
        try:
            return self.rowLabels[row]
        except IndexError:
            return str(row + 1)

    #--------------------------------------------------
    # Methods added for demo purposes.
    # The physical moving of the cols/rows is left to the implementer.
    # Because of the dynamic nature of a wxGrid the physical moving of
    # columns differs from implementation to implementation
    # Move the column
    def MoveColumn(self,frm,to):
        grid = self.GetView()
        if grid:
            # Move the identifiers
            old = self.identifiers[frm]
            del self.identifiers[frm]
            if to > frm:
                self.identifiers.insert(to-1,old)
            else:
                self.identifiers.insert(to,old)
            # Notify the grid
            grid.BeginBatch()

            msg = gridlib.GridTableMessage(
                    self, gridlib.GRIDTABLE_NOTIFY_COLS_INSERTED, to, 1
                    )
            grid.ProcessTableMessage(msg)
            msg = gridlib.GridTableMessage(
                    self, gridlib.GRIDTABLE_NOTIFY_COLS_DELETED, frm, 1
                    )
            grid.ProcessTableMessage(msg)

            grid.EndBatch()
    # Move the row
    def MoveRow(self,frm,to):
        grid = self.GetView()
        if grid:
            # Move the rowLabels and data rows
            oldLabel = self.rowLabels[frm]
            oldData = self.data[frm]
            del self.rowLabels[frm]
            del self.data[frm]
            if to > frm:
                self.rowLabels.insert(to-1,oldLabel)
                self.data.insert(to-1,oldData)
            else:
                self.rowLabels.insert(to,oldLabel)
                self.data.insert(to,oldData)
            # Notify the grid
            grid.BeginBatch()
            msg = gridlib.GridTableMessage(
                    self, gridlib.GRIDTABLE_NOTIFY_ROWS_INSERTED, to, 1
                    )
            grid.ProcessTableMessage(msg)
            msg = gridlib.GridTableMessage(
                    self, gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, frm, 1
                    )
            grid.ProcessTableMessage(msg)

            grid.EndBatch()

    ################################################################
    ## for setting row and col and data, making this general-purpose
    ################################################################

    def SetRowLabels(self, newlabel, copy=True):
        self.rowLabels = newlabel[:] if copy else newlabel

    def SetColLabels(self, newmap, copy=True):
        self.colLabels = newmap.copy() if copy else newmap

    def SetData(self, newdata):
        self.data = newdata

    def SetIdentifiers(self, newid, copy=True):
        self.identifiers = newid[:] if copy else newid

#---------------------------------------------------------------------------
class DragableGrid(gridlib.Grid):
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1)
        self.table = CustomDataTable()

        # Enable Column moving
        gridmovers.GridColMover(self)
        self.Bind(gridmovers.EVT_GRID_COL_MOVE, self.OnColMove, self)
        # Enable Row moving
        gridmovers.GridRowMover(self)
        self.Bind(gridmovers.EVT_GRID_ROW_MOVE, self.OnRowMove, self)

    def SetTable(self, tbl):
        if issubclass(type(tbl), TitledTable):
            tgttbl = self.table
            ids = tbl.titleline
            # py2.6 doesn't have dict comprehension...
            # here's a (mostly dirty) hack when i don't want to fix the columns
            # to some particular things...
            collabels = dict(zip(ids, ids))
            data = [dict(zip(ids, row)) for row in tbl]
            # populate the CustomDataTable
            tgttbl.SetIdentifiers(ids)
            tgttbl.SetColLabels(collabels)
            # to support row dragging, rowlabels must be present.
            tgttbl.SetRowLabels([str(i) for i in range(1, len(tbl.rows) + 1)])

            tgttbl.SetData(data)
            # The second parameter means that the grid is to take ownership of
            # the table and will destroy it when done.  Otherwise you would
            # need to keep a reference to it and call it's Destroy method
            # later.
            gridlib.Grid.SetTable(self, tgttbl, True)
        else:
            gridlib.Grid.SetTable(self, tbl, True)

    # Event method called when a column move needs to take place
    def OnColMove(self,evt):
        frm = evt.GetMoveColumn()       # Column being moved
        to = evt.GetBeforeColumn()      # Before which column to insert
        self.GetTable().MoveColumn(frm,to)
    # Event method called when a row move needs to take place
    def OnRowMove(self,evt):
        frm = evt.GetMoveRow()          # Row being moved
        to = evt.GetBeforeRow()         # Before which row to insert
        self.GetTable().MoveRow(frm,to)


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
