#!/usr/bin/env python
# -*- coding: utf-8 -*-
# JNMaster / dailyinfo / weather info engine
# XXX This is VERY DEEPLY BOUND TO JNRain atm, refactor this to call into
# univlib!!
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

# for now it's simply a scraper that looks at jnrain home page

import re

from gingerprawn.api.webop import automated as auto

_BASEURL = 'http://202.195.144.15/wForum/index.php'
_CSSPATH = 'td.TopLighNav1 font'
_WEATHER_PAT = (ur'^(?P<month>\d{2})月(?P<day>\d{2})日 '
                ur'白天 (?P<dayweather>.+) (?P<daytemp>-*\d+)℃ '
                ur'夜间 (?P<nightweather>.+) (?P<nighttemp>-*\d+)℃$'
                )
_WEATHER_CATCHER = re.compile(_WEATHER_PAT)

################################################################

def get_weather():
    bot = auto.Automator(_BASEURL)
    req_weather_with_finalize(bot)
    bot.execute()
    return bot.result['weather']

def __filter_helper(br, buf, src_var, tgt_var):
    # 1st make plain texts for matching
    tmplist = ['\n'.join(i.itertext()).replace(u'\xa0', u' ')
            for i in buf[src_var]]
    # 2nd match 'em against our catcher
    matches = [_WEATHER_CATCHER.match(i) for i in tmplist]
    # 3rd get the (sorted) results...
    # sometimes jnrain's weather has (rather) corrupted date such as 02/30
    # so we have to discard date info regardless of its correctness
    # structure of the final result is
    # {'day':   (dayweather, daytemp), 'night': (nightweather, nighttemp), }
    # but we have to do a Schwartzian transform first, hence the added date
    # tuple there below
    result = [((int(i.group('month')), int(i.group('day'))),
                    {'day': (i.group('dayweather'), int(i.group('daytemp'))),
                     'night': (i.group('nightweather'),
                               int(i.group('nighttemp'))),
                     })
            for i in matches if i is not None]
    result.sort()
    result = [i[1] for i in result]

    return (True, {tgt_var: result}, )


def req_weather(tgt):
    tgt.add_task(auto.OP_STORE_NODE, 'page')
    tgt.add_task(auto.OP_CSSSELECT, 'page', _CSSPATH, 'nodes')
    tgt.add_task(auto.OP_CUSTOM, __filter_helper, 'nodes', 'weather')

def req_weather_with_finalize(tgt):
    req_weather(tgt)
    tgt.add_task(auto.OP_CLOSE)


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
