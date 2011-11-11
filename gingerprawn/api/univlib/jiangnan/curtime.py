#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.univlib.jiangnan / determining educational week
# Original code was contributed by Chen Huayue (TheC@JNRain), then adapted by
# Wang Xuerui (xenon@JNRain).
# XXX This file is to be moved to backend as its functionality can be shared
#
# Copyright (C) 2011 Chen Huayue <489412949@qq.com>
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

from datetime import datetime as dt # danteng, ballache (=
from datetime import date as d # ...
from datetime import timedelta

now = dt.now
today = now
delta1 = timedelta(1)

# TODO: CHANGE THIS VAR'S NAME TO STH MORE ACCURATE!
_WEEKDAYS = [u'星期一', u'星期二', u'星期三', u'星期四', u'星期五',
         u'星期六', u'星期日', ]

def first_day():
    return dt(now().year, 1, 1)

def today_weekday():
    return today().weekday()

def tomorrow():
    return now() + delta1

def tomorrow_weekday():
    return tomorrow().weekday()

def curweek(today=None):
    if today is None:
        # Default to today, else use that day as "today"
        today = now()
    if type(today) is d:
        # who can devise a greater conversion?
        today = dt(today.year, today.month, today.day)

    first_d = first_day()
    return ((today - first_d).days - (7 - first_d.weekday())) / 7 + 1

def weekoffset(origin, today=None, start=1):
    '''\
    Taking the origin's week as the start-th week, calculate the current
    week's ordinal.
    '''
    # 1-based.
    return curweek(today) - curweek(origin) + start

def schoolyear(y, m):
    return y if m >= 9 else y - 1

def schoolyear_str(y, m):
    schoolyr = schoolyear(y, m)
    return '%d-%d' % (schoolyr, schoolyr + 1, )

def schoolterm(m):
    return 2 if 2 <= m <= 8 else 1

def schoolterm_str(m):
    return str(schoolterm(m))

def curr_schoolyear():
    today = now()
    return schoolyear(today.year, today.month)

def curr_schoolyear_str():
    today = now()
    return schoolyear_str(today.year, today.month)

def curr_schoolterm():
    today = now()
    return schoolyear(today.month)

def curr_schoolterm_str():
    today = now()
    return schoolterm_str(today.month)

# test purpose.
def main():
    TimeNowYear=TimeNow.year
    TimeNowMonth=TimeNow.month
    TimeNowWeek=((TimeNow-TimeFirstDay).days-(7-TimeFirstDay.weekday()))/7+1

    TimeEduYear=schoolyear(TimeNowYear, TimeNowMonth)
    TimeEduTerm=schoolterm(TimeNowMonth)

    print u"现在是%s年%s月，第%s周" % (TimeNowYear,TimeNowMonth,TimeNowWeek)
    print _WEEKDAYS[TimeNow.weekday()]
    print u"教学%s学年第%s学期" % (TimeEduYear,TimeEduTerm)

if __name__ == '__main__':
    main()


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
