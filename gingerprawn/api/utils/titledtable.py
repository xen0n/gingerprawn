#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.utils / titled table class
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

'''\
Titled table class provided for easing table processing.
'''

class TitledTable(object):
    def check_integrity(self, row=None):
        '''\
        if *row* is ``None``\ , check the whole table. Otherwise only check
        that row.
        Returns ``None`` if passed, or raises ``ValueError`` if failed.
        '''
        if row is None:
            for i in self.rows:
                if len(i) != self.titlelen:
                    raise ValueError('Column count mismatch')
            return
        else:
            if len(row) == self.titlelen:
                return
            raise ValueError('Column count mismatch')

    def check_slice_integrity(self, rows):
        l = self.titlelen
        for i in rows:
            if len(i) != l:
                raise ValueError('Column count mismatch')

    def __init__(self, content=None):
        if content is not None:
            # self.titleline = tuple(content[0]) # immutable for now
            # mutable now for supporting dragable grid
            self.titleline = content[0][:]
            self.titlelen = len(self.titleline)
            self.rows = content[1:] # Note this can contain mutable objs
            self.check_integrity()
            return
        self.titleline = ()
        self.titlelen = 0
        self.rows = []

    def __iadd__(self, op1):
        # op1 is one row to be inserted
        # first a little sanity check
        self.check_intgrity(op1)
        self.rows.append(op1)

    def set_title(self, title):
        if self.titleline:
            raise ValueError('can only set title when table is empty')
        self.titleline = tuple(title)
        self.titlelen = len(title)

    def get_field(self, fieldname):
        idx = self.titleline.index(fieldname) # this will auto-raise exception
        return [tr[idx] for tr in self.rows]

    def get_fields(self, fields):
        return [self.get_field(i) for i in fields]

    def __getitem__(self, idx):
        typ = type(idx)
        if typ is unicode or typ is str:
            return self.get_field(idx)
        return self.rows[idx] # supports stride too

    def __setitem__(self, idx, thing):
        self.check_integrity(thing)
        self.rows[idx] = thing

    def __getslice__(self, lo, hi):
        return self.rows[lo:hi]

    def __setslice__(self, lo, hi, newslice):
        self.check_slice_integrity(newslice)
        self.rows[lo:hi] = newslice

class RowSpanTitledTable(object):
    '''\
    This is a titled table supporting cells that span across multiple rows.
    Currently this table *must* be initialized with data, and is
    *immutable*\ .

    Because of the very different interface, it's now a distinct class,
    although there is a high possibility that this class becomes a subclass
    of ``TitledTable`` again.

    Table cell is of format ``(content, rowspan)``\ .
    '''
    def __init__(self, content):
        title = content[0]
        self.titleline = tuple([td for td, rowspan in title])
        self.titlelen = len(title)

        # Note content can contain mutable objs
        self.processed = self._try_to_formulate(content[1:])

    def _try_to_formulate(self, rows):
        # Numbers of remaining row to skip for each column
        remaining_rows = [0] * self.titlelen
        processed = []

        for row_idx, tr in enumerate(rows):
            # According to the HTML semantics, the rowspan property makes the
            # following (rowspan - 1) row(s) belonging to the current column
            # unoccupied (non-existent), so every cell must occur at a position
            # where remaining_rows[col] == 0. If the number of cells in this
            # row compares unequal to the number of 0's in remaining_rows,
            # there must be a mistake in the input data.
            if len(tr) != remaining_rows.count(0):
                # error, integrity check failed
                raise ValueError('cell count mismatch for row %d: '
                                 'len(tr) = %d, but count of 0 is %d' %
                                 (row_idx, len(tr), remaining_rows.count(0),
                                 ))

            # map cells in the current row to appropriate positions
            tmp, i = [], 0
            for col_idx, rem in enumerate(remaining_rows):
                if rem != 0:
                    # Skip cells that are non-existent (overlapped).
                    continue
                # remaining row to skip for this column is now 0, meaning a new
                # cell belong here. Insert it at the appropriate position.
                tmp.append((col_idx, tr[i]))
                i += 1
            processed.append(tmp)

            # update buffer for the next row
            # td[1] is rowspan
            # can only use this non-Pythonic construct because the conditions
            # are rather complex here, and the list **needs to be updated**
            i = 0
            for col_idx in range(len(remaining_rows)):
                if remaining_rows[col_idx] != 0:
                    # skip over nonexistent cells, also update counter
                    remaining_rows[col_idx] -= 1
                    continue

                # add rowspan, going past the current row (hence the -1 here)
                remaining_rows[col_idx] += tr[i][1] - 1
                i += 1 # I always forget this
            print 'after row %d:\t%s' % (row_idx, `remaining_rows`) # DEBUG

        return processed


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
