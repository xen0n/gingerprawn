#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.cooker / shrimp icon manager
# simple imagelist manipulation with "named image" support using a dict
# without wx dependency
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

from gingerprawn.api import logger
logger.install()

ICON_WIDTH = ICON_HEIGHT = 64
ICON_IMAGELIST = []
ICON_NAMEMAP = {}

from gingerprawn.api.cooker.builtin_icons import UNKNOWN_ICON

def init():
    # Still this has to happen after wx.App's creation
    add_icon('<unknown_icon>', UNKNOWN_ICON)

def add_icon(shrimp, img):
    if img is None:
        logwarning('Icon not specified for shrimp %s, using unknown', shrimp)
        ICON_NAMEMAP[shrimp] = 0
        return 0
    # actual icon data given. img is a PyEmbeddedImage
    ICON_IMAGELIST.append(img.GetBitmap())
    idx = len(ICON_IMAGELIST) - 1
    ICON_NAMEMAP[shrimp] = idx
    # logdebug('Icon added for shrimp %s, idx = %d', shrimp, idx)
    return idx

def get_icon_index(shrimp):
    return ICON_NAMEMAP.get(shrimp, 0)

def get_bitmap(shrimp):
    return ICON_IMAGELIST[ICON_NAMEMAP.get(shrimp, 0)]


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
