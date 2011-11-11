#!/usr/bin/env python
# -*- coding: utf-8 -*-
# JNMaster / academic / auto reminder implementation
# this will talk to jwxt's autoremind backend
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

import threading

import wx

# dummy i18n
_ = lambda x: x

from gingerprawn.api import logger
logger.install()

# university academic affairs system's interface
from gingerprawn.api import univlib
jwxt = univlib.current.jwxt

# date and time processing
curtime = univlib.current.curtime

REMINDER_SECTION = 'reminder'

#############################################################################
## SEPARATOR BETWEEN DECLARATIONS AND MIDDLE-END
#############################################################################

def get_autoremind_cfg(cfg, set_initials=True):
    ## NOTE: this piece of code resides here, because the autostart part
    ## also wants to use the configuration, but it's not academic_main.
    ## so the init, while still takes place every time this shrimp is
    ## brought up, is independent of any frame.
    ## This position may become the coding standard... let time prove its
    ## correctness...
    ## MOVED.
    refdate = cfg.get_obj(REMINDER_SECTION, 'refdate', None)
    refweek = cfg.get(REMINDER_SECTION, 'refweek', None)
    is_enabled = cfg.get(REMINDER_SECTION, 'enabled', None)
    if refdate is None or refweek is None or is_enabled is None:
        # loading of setting failed, see if the caller is to request
        # some initial values for setting dialog.
        if set_initials:
            refdate = curtime.now()
            refweek = 1
            is_enabled = False
            return {'refdate': refdate,
                    'refweek': refweek,
                    'is_enabled': is_enabled,
                    }
        else:
            # the caller is in action, throw exc
            raise AttributeError('autoremind parameter not properly set')
    else:
        refweek = int(refweek)
        is_enabled = is_enabled.lower()

    # see how forgiving this code is...
    if is_enabled == 'yes' or is_enabled == 'true':
        is_enabled = True
    else:
        is_enabled = False
    return {'refdate': refdate,
            'refweek': refweek,
            'is_enabled': is_enabled,
            }

#############################################################################
## SEPARATOR BETWEEN MIDDLE-END AND (MAINLY) GUI IMPLEMENTATION (FRONTEND)
#############################################################################

try:
    from agw import toasterbox as TB
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.toasterbox as TB

TOASTER_LINGER_MILLISECONDS = 8000 # 8 seconds
TOASTER_SCROLLSPEED = 2
TOASTER_SIZE_X = 300
TOASTER_SIZE_Y = 200
SCREEN_RIGHT_MARGIN = 10
SCREEN_BOTTOM_MARGIN = 48 # consider most taskbars' bottom position.

# The prompts used.
NORMAL_TEMPLATE = (u'明天是第 %(weekord)d 教学周，%(weekday)s，该上的课有：\n'
                  u'%(courses)s\n'
                  u'作业做完了吗？\n\n'
                  u'如果教学周推算不准，请在主程序中调整…\n'
                  u'单击来关闭我～ 祝学习愉快！ O(∩_∩)O'
                  )

NOCOURSE_TEMPLATE = (u'明天是第 %(weekord)d 教学周，%(weekday)s，\n'
                     u'没有课唉！O(∩_∩)O 也许可以稍微休息一下了，呼～\n\n'
                     u'如果教学周推算不准，请在主程序中调整…\n'
                     u'单击来关闭我～ 好好休息才能好好工作！'
                     )

COURSE_LINE_FMT = u'%(name)s，%(start)d 到 %(end)d 节，在 %(loc)s'

def format_course(course):
    return COURSE_LINE_FMT % {
            'name': course['name'],
            'loc': course['location'],
            'start': course['duration'][0],
            'end': course['duration'][1],
            }

def format_prompt(weekord, weekday, courses):
    if courses:
        courses_str = u'；\n'.join(format_course(course) for course in courses)
        prompt_template = NORMAL_TEMPLATE
    else:
        courses_str = u''
        prompt_template = NOCOURSE_TEMPLATE
    return prompt_template % {
            u'weekord': weekord,
            u'weekday': curtime._WEEKDAYS[weekday],
            u'courses': courses_str,
            }

class autoremind_frame(wx.Frame):
    def fireup_toaster(self, prompt):
        tb = TB.ToasterBox(self,
                TB.TB_SIMPLE, TB.TB_DEFAULT_STYLE, TB.TB_ONCLICK)
        # Set some styles.
        tb.SetPopupPauseTime(TOASTER_LINGER_MILLISECONDS)
        tb.SetPopupScrollSpeed(TOASTER_SCROLLSPEED)

        # Set up position and size.
        # TODO: refactor this useful tidbit of code into a separate fn!
        tb.SetPopupSize((TOASTER_SIZE_X, TOASTER_SIZE_Y))

        screenX = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        screenY = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
        # for now the position is fixed at the bottom-right corner of
        # screen. maybe changing this is interesting
        # position is the topleft corner of toasterbox, remember that!
        posX = screenX - TOASTER_SIZE_X - SCREEN_RIGHT_MARGIN
        posY = screenY - TOASTER_SIZE_Y - SCREEN_BOTTOM_MARGIN
        tb.SetPopupPosition((posX, posY))

        # No background bitmap... just solid color.
        # TODO: make this color portable across different platforms
        tb.SetPopupBackgroundColour(wx.SystemSettings.GetColour(
                    wx.SYS_COLOUR_3DFACE))
        tb.SetPopupBitmap()

        # The content! a Unicode thing...
        tb.SetPopupText(prompt)

        # GO DISPLAY!
        tb.Play()

    def do_autoremind(self, prnt, cfg_obj, jwxt_cache):
        # using a local var is OK because this class is one-use (=
        affairs = jwxt.JiangnanAcademicAffairs(jwxt_cache)
        # unlikely to cause exc here because cfg_obj is already there...
        ret = affairs.prepare2remind()
        if not ret:
            # not prepared yet, cannot autoremind!
            loginfo('autoremind cache empty,  quitting')
            return

        # OK. Do some more preparation.
        try:
            reminder_cfg = get_autoremind_cfg(cfg_obj, set_initials=False)
        except AttributeError:
            # parameters not properly set
            loginfo('autoremind parameters not properly set, quitting')
            return

        refdate = reminder_cfg['refdate']
        refweek = reminder_cfg['refweek']
        is_enabled = reminder_cfg['is_enabled']

        if is_enabled:
            schoolweek = curtime.weekoffset(refdate, start=refweek)
            weekday = curtime.tomorrow_weekday()

            courses = affairs.query_day_courses(
                    curtime.curr_schoolyear_str(),
                    curtime.curr_schoolterm_str(),
                    schoolweek,
                    weekday)

            prompt = format_prompt(schoolweek, weekday, courses)
            self.fireup_toaster(prompt)
        else:
            #autoremind disabled, go away!
            pass

    def __init__(self, prnt, cfg_obj, jwxt_cache):
        wx.Frame.__init__(self, prnt)

        self.do_autoremind(prnt, cfg_obj, jwxt_cache)

        # well... is __init__ a dtor?? (=
        # TODO: This timer will cause the frame to destroy after LINGER ms's,
        # no matter how early the user clicked.
        # Fix this if have time.
        self._destroy_timer = wx.PyTimer(self.delayed_destroy)
        self._destroy_timer.Start(TOASTER_LINGER_MILLISECONDS)

    def delayed_destroy(self):
        self._destroy_timer.Stop()
        self.Destroy()

def invoke(prnt, cfg_obj, jwxt_cache):
    # We can directly do GUI calls, because the call to this function
    # is to be done by wx.CallAfter.
    frame = autoremind_frame(prnt, cfg_obj, jwxt_cache)


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
