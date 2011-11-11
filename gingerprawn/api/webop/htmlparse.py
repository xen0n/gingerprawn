#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.webop / HTML parsing high-level helpers
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

import re

from lxml import html

from gingerprawn.api.utils.titledtable import TitledTable, RowSpanTitledTable

# this is dead (and incorrect) code, remove in next rev
# HTML_NEWLINE = re.compile(r'<br\s*/*>')

# helpers...
def fromstring(s):
    return html.fromstring(s)

# this fn actually reduced code replication
def elem2text(node):
    return u'\n'.join(node.itertext()).replace(u'\xa0', u'')

#############################################################################
# Wrappers and interface functions
#

# Easy interface...
def parse_into_table(tbl_node, filter_fn=None):
    tbl_list = parse_table_into_list(tbl_node, filter_fn)
    return TitledTable(tbl_list)

def parse_into_rowspantable(tbl_node, filter_fn=None):
    tbl_list = parse_rowspantable_into_list(tbl_node, filter_fn)
    return RowSpanTitledTable(tbl_list)

# Wrappers.
#
# These functions choose the appropriate version of worker function,
# not needing a dummy preprocessor when there is no need, thus reducing
# function call overhead.

def parse_table_into_list(tbl_node, preprocessor=None):
    if preprocessor is None:
        return _parse_table_into_list_nopre(tbl_node)
    else:
        return _parse_table_into_list_pre(tbl_node, preprocessor)

def parse_rowspantable_into_list(tbl_node, preprocessor=None):
    if preprocessor is None:
        return _parse_table_into_list_nopre(tbl_node)
    else:
        return _parse_table_into_list_pre(tbl_node, preprocessor)

#############################################################################
# actual functions
#

#########################
# parse_table_into_list #
#########################
def _parse_table_into_list_pre(tbl_node, preprocessor):
    result = []

    for rowidx, tr in enumerate(tbl_node.getchildren()):
        tmp_row = []

        for colidx, td in enumerate(tr):
            # Preliminary processing to cope with some of the known
            # string problems.
            txt = elem2text(td).strip(' \n')

            # Enhanced preprocessing support.
            # XXX: PERFORMANCE HIT WHEN INPUT SIZE IS LARGE
            filtered, cooked = preprocessor(rowidx,colidx, txt)
            if not filtered:
                tmp_row.append(cooked)

        result.append(tmp_row)
    return result

def _parse_table_into_list_nopre(tbl_node):
    result = []

    for tr in tbl_node.getchildren():
        tmp_row = []

        for td in tr:
            # Preprocessing removed to save function invocations.
            # Only keeping the vital processing (to prevent possible
            # UnicodeEncodeError)
            tmp_row.append(elem2text(td).strip(' \n'))

        result.append(tmp_row)
    return result

################################
# parse_rowspantable_into_list #
################################

def _parse_rowspantable_into_list_pre(tbl_node, preprocessor):
    result = []

    for rowidx, tr in enumerate(tbl_node.getchildren()):
        tmp_row = []

        for colidx, td in enumerate(tr):
            txt = elem2text(td)
            filtered, cooked = preprocessor(rowidx,colidx, txt)

            if not filtered:
                tmp_row.append(
                        (txt,
                         int(td.attrib.get('rowspan', 1)), ) # rowspan
                         )

        result.append(tmp_row)
    return result

def _parse_rowspantable_into_list_nopre(tbl_node):
    result = []

    for tr in tbl_node.getchildren():
        tmp_row = []

        for td in tr:
            tmp_row.append(
                    (elem2text(td), # txt, distinct var is unneeded
                     int(td.attrib.get('rowspan', 1)), ) # rowspan
                     )

        result.append(tmp_row)
    return result

# MAYBE: remove_tags

# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
