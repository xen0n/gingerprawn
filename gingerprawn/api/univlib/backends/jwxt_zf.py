#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.univlib.backends / Academic ops -- talking to ZFSOFT systems
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

__all__ = ['ZFAcademicAffairs',
           ]

import re

# no need to depend on urllib{,2} directly
from gingerprawn.api.webop import automated as auto

from jwxt_base import AcademicAffairsBase

# for more abstract curriculum processing
# TitledTable is not used *here* because that logic is in shrimp...
from gingerprawn.api.utils.titledtable import RowSpanTitledTable

# generalize encoding
PAGE_ENCODING = 'gb18030'

ROLE_DEPT = u'部门'.encode(PAGE_ENCODING)
ROLE_STUDENT = u'学生'.encode(PAGE_ENCODING)
ROLE_TEACHER = u'教师'.encode(PAGE_ENCODING)
ROLE_GUEST = u'访客'.encode(PAGE_ENCODING)

_BASIC_INFO_RE = re.compile(ur'^(?P<studno>\d+)\s+(?P<name>.+)同学$')
_PASSWDERR_MSG = u"<script>alert('密码错误！！');</script>".encode('gbk')

# FIXED: small problem with that /\d+(?:,\d+)*/ thing...
# AGAIN IMPROVED: when a course has complex span info related to week, its
# info string becomes somewhat duplicated in its content. So the beginning
# and end limiters ^ and $ are gone.
# Now this RE is meant to be used in the finditer way...

# UPDATED 20110828: Just noticed that the jwxt output changed, adding a line
# indicating course type like A(Univ-wide,Mandatory), B(College, Mandatory),
# K(School-wide,Elective)...
# -- OT: who can tell me the right translation of 校定/院定 and 选修/必修? OvO
_PERIOD_INFO_RE = re.compile(
                  (ur'(?P<coursename>.*)\n'
                   ur'(?P<coursetype>.*)\n'
                   ur'(?:周.第(?P<duration>\d+(?:,\d+)*)节)*'
                   ur'\{第(?P<weekspan>\d+-\d+)周(?:\|(?P<weekprop>.*))*\}\n'
                   ur'(?P<teacher>.*)\n'
                   ur'(?P<location>.*)'
                   ))

# The 1st and 2nd Teaching Buildings' canonical classroom number
# is [12][ABCD]\d{3}, but just using \w is enough.
_LOCATION_SIMPLIFIER_RE = re.compile(ur'\w{5}')

################################################################
# INTERFACE CLASS

class ZFAcademicAffairs(AcademicAffairsBase):
    def set_user_info(self, usr, psw, typ=ROLE_STUDENT):
        self._usr = usr
        self._psw = psw
        self._typ = typ

    def do_login(self):
        req_login(self._bot, self._usr, self._psw, self._typ)
        try:
            self._bot.execute()
        except auto.URLError, e:
            self.error_reason = 'network'
            self.exc = e
            raise RuntimeError('Network error')

        if not self._bot.result['psw_status']:
            self.error_reason = 'password'
            raise ValueError('Password incorrect!')

        self._lastop = 'mainpage'
        self.__sect_curricula = 'curricula_%s' % self._usr
        self.__sect_scores = 'scores_%s' % self._usr

        # Store the main page for future log-out.
        self.__mainpage = self._bot.result['mpage']

        return self._bot.succeeded()

    def do_logout(self):
        # FIXED. Now it works.
        # self.chk_last_op()
        req_logout(self._bot, self.__mainpage)
        self._bot.execute()
        self._lastop = 'logout'
        return self._bot.succeeded()

    def get_basicinfo(self):
        self.chk_last_op()
        req_basic_info(self._bot)

        try:
            self._bot.execute()
        except auto.URLError, e:
            self.error_reason = 'network'
            self.exc = e
            raise RuntimeError('Network error')

        if not self._bot.succeeded():
            raise RuntimeError('basicinfo parsing failed')
        self.basic_info = (self._bot.result['studno'],
                           self._bot.result['name'])
        self._lastop = 'mainpage'
        return self.basic_info

    def prepare4curriculum(self):
        self.chk_last_op()
        req_prepare_curriculum(self._bot)
        try:
            self._bot.execute()
        except auto.URLError, e:
            # this operation can use cached result...
            pass

        self._lastop = 'curriculum'

        if self._bot.succeeded():
            # Use the actual form data.
            yrs = self.curriculum_years = self._bot.result['years']
            tms = self.curriculum_terms = self._bot.result['terms']
            self.curriculum_defaults = (
                    self._bot.result['year_selected'],
                    self._bot.result['term_selected']
                    )
        else:
            # Fetching of current years and terms failed, revert to cached
            # result
            yrs = self._cache.get_obj(self.__sect_curricula, 'yrs', None)
            tms = self._cache.get_obj(self.__sect_curricula, 'tms', None)
            if yrs is None or tms is None:
                raise RuntimeError('year and term fetch failed!')

            self.curriculum_years = yrs
            self.curriculum_terms = tms

            # Here we can give sensible defaults since yrs and tms are ready
            self.curriculum_defaults = self._cache.get_obj(
                    self.__sect_curricula, 'def', (yrs[0], tms[0], ))

        # self.curriculum = {}
        # new: cached curriculum...
        if self._cache is not None:
            self.curriculum = self._cache.get_obj(self.__sect_curricula,
                    'tbls', {})
            self._cache.ensure_section(self.__sect_curricula)
            self._cache.set_obj(self.__sect_curricula, 'yrs', yrs)
            self._cache.set_obj(self.__sect_curricula, 'tms', tms)
            self._cache.set_obj(self.__sect_curricula, 'def',
                    self.curriculum_defaults)
        else:
            self.curriculum = {}

        return (yrs, tms, )

    def get_curriculum(self, yr_sel, term_sel, raw=False):
        ## UPDATED 20110828: jwxt changed to not giving us a useful empty
        ## entry in the year selection box, so we need to employ the same
        ## mechanism used to workaround the term box quirk in order to
        ## survive this change...
        ## Mostly same code responsible for choosing workaround entries
        ## is added to compensate the year box problem.

        self.chk_last_op('curriculum')

        # sanity check
        if yr_sel not in self.curriculum_years:
            raise ValueError("invalid schoolyear selected")
        if term_sel not in self.curriculum_terms:
            raise ValueError("invalid term selected")
        # chk passed, do real work

        # for selecting a term for workarounding jwxt quirk...
        from random import choice, seed
        seed()

        # first check cache...
        if (yr_sel, term_sel) in self.curriculum:
            return True
        yr_idx = self.curriculum_years.index(yr_sel)
        term_idx = self.curriculum_terms.index(term_sel)

        # term_workaround_idx = (term_idx + 1) % len(self.curriculum_terms)

        yr_workarounds = [i for i in range(len(self.curriculum_years))
                if i != yr_idx and i != self.curriculum_defaults[0]]

        term_workarounds = [i for i in range(len(self.curriculum_terms))
                if i != term_idx and i != self.curriculum_defaults[1]]

        # this will IndexError if only 2 are present, but at present there're
        # 3. mark this as TODO
        # TODO: fix this possible IndexError
        yr_alt = self.curriculum_years[choice(yr_workarounds)]
        term_alt = self.curriculum_terms[choice(term_workarounds)]

        req_curriculum_page(self._bot, yr_sel, term_sel, yr_alt, term_alt,
                            raw=raw)

        self._bot.execute()
        if not (yr_sel, term_alt) in self.curriculum:
            self.curriculum[(yr_sel, term_alt)] = self._bot.result['alt_c_tbl']
        self.curriculum[(yr_sel, term_sel)] = self._bot.result['c_tbl']

        # update cache.
        if self._cache is not None:
            self._cache.set_obj(self.__sect_curricula, 'tbls', self.curriculum)
            # support for autoremind: update lookup table
            self.update_autoremind()

        return self._bot.succeeded()

    def prepare4scores(self):
        self.chk_last_op()
        try:
            if self._cache is not None:
                self.scores = self._cache.get_obj(self.__sect_scores,
                        'scores', None)
            # TODO: improve this cache hit test
            if self.scores is not None:
                # must maintain the correct flow of status
                self._lastop = 'scores'
                return True
        except AttributeError:
            pass

        req_prepare_scores(self._bot)
        self._bot.execute()
        self._lastop = 'scores'
        return self._bot.succeeded()

    def get_scores(self, *args, **kwargs):
        self.chk_last_op('scores')

        # Check the in-object cache first...
        try:
            if self.scores is not None:
                # Cache hit, immediately return
                return True
        except AttributeError:
            # cache is not present or maybe something mysterious happened
            pass

        # Cache miss. Actually request for the scores page.
        req_scores(self._bot)
        self._bot.execute()

        # Update in-object cache...
        self.scores = self._bot.result['scores']
        if not self._bot.succeeded():
            return False # early fail, no need to update cache.

        # update external cache if one is present
        if self._cache is not None:
            self._cache.ensure_section(self.__sect_scores)
            self._cache.set_obj(self.__sect_scores, 'scores', self.scores)

        # must return a status
        return True

    def update_autoremind(self):
        result = {}
        for k, tbl in self.curriculum.items():
            result[k] = parse_curriculum(tbl)
        self._cache.ensure_section('reminder')
        self._cache.set_obj('reminder', 'weeks_cache', result)

    def prepare2remind(self):
        if self._cache is None:
            # this is a bug in invoker's logic...
            raise RuntimeError(
                    'reminder feature can only work with predownloaded data')

        self.reminder_weeks = self._cache.get_obj('reminder',
                'weeks_cache', None)

        if self.reminder_weeks is None:
            # nothing cached yet...
            return False
        return True

    def query_day_courses(self, yrstr, termstr, weekord, weekday):
        try:
            lookup_tbl = self.reminder_weeks[(yrstr, termstr)]
        except KeyError:
            raise ValueError('not found in cache')

        # directly filter out other columns
        lookup_tbl = lookup_tbl[weekday]

        result = []
        for course in lookup_tbl:
            try:
                period = course['weeks'][weekord]
            except KeyError:
                # not present in this week...
                continue

            # period's structure is like {
            #   'duration': dur,
            #   'location': location,
            #   'weekprop': weekprop,
            #   }
            # combining with course's structure, {
            #   'name': coursename,
            #   'teacher': teacher,
            #   'weeks': weeks,
            #   }
            # gives us a result like below...
            tmp = {'name': course['name'],
                   'location': period['location'],
                   'duration': period['duration'],
                   }
            result.append(tmp)
        return result


################################################################
## IMPLEMENTATION OF AUTOMATOR'S VARIOUS MOVES
################################################################

def req_login(tgt, usr, psw, typ):
    def _chk_passwd(br, buf, src_var, tgt_var):
        if _PASSWDERR_MSG in buf[src_var]:
            return (False, {tgt_var: False}, )
        else:
            return (True, {tgt_var: True}, )

    # look at those default ID's...
    tgt.add_task(auto.OP_SELECTFORM, 'form1')
    tgt.add_task(auto.OP_FILLFORM, {
            'TextBox1': usr,
            'TextBox2': psw,
            'RadioButtonList1': [typ],
            })
    tgt.add_task(auto.OP_SUBMIT)

    # Store the page, for logout
    tgt.add_task(auto.OP_STORE_CONTENT, 'mpage') # , False)
    tgt.add_task(auto.OP_CUSTOM, _chk_passwd, 'mpage', 'psw_status')

def req_logout(tgt, page):
    # FIXED: that damn form seems to have escaped from mech and lxml!
    # the main page right after successful login is restored before
    # logout, so the form is now there!

    # this bit of "safe logout" is implemented using Javascript
    # so must analyze this by hand, fortunately this is trivial
    tgt.add_task(auto.OP_MODIFY_RESPONSE, page)
    tgt.add_task(auto.OP_SELECTFORM, 'Form1')
    tgt.add_task(auto.OP_EVENTTARGET, 'likTc')
    tgt.add_task(auto.OP_SUBMIT)

def req_basic_info(tgt):
    def _automator_basicinfo_helper(br, buf, src_var):
        # this extends Automator's functionality, adding the capability to parse
        # basic info string into student number and name.
        try:
            studno, name = parse_basicinfo_str(buf[src_var].text)
        except ValueError:
            return (False, {}, )
        return (True, {'studno': studno, 'name': name}, )

    tgt.add_task(auto.OP_STORE_NODE, 'front')
    tgt.add_task(auto.OP_CSSSELECT, 'front', '#xhxm', 'basicinfo_spans')
    tgt.add_task(auto.OP_CHOOSEONE, 'basicinfo_spans', 0, 'basicinfo_str')
    tgt.add_task(auto.OP_CUSTOM, _automator_basicinfo_helper, 'basicinfo_str')

def req_prepare_curriculum(tgt):
    def _automator_curriculum_helper(br, buf):
        # parses schoolyear and (1st, 2nd, 3rd) term info
        xnd = br.form.find_control('xnd')
        xqd = br.form.find_control('xqd')
        xnd_list = [opt.attrs['value'] for opt in xnd.get_items()]
        xqd_list = [opt.attrs['value'] for opt in xqd.get_items()]

        xnd_list = [i for i in xnd_list if i is not None]
        selected_xnd = [opt.attrs['value'] for opt in xnd.get_items()
                if opt.attrs.get('selected', '') == 'selected'][0]
        selected_xqd = [opt.attrs['value'] for opt in xqd.get_items()
                if opt.attrs.get('selected', '') == 'selected'][0]

        return (True, {'years': xnd_list, 'terms': xqd_list,
                       'year_selected': selected_xnd,
                       'term_selected': selected_xqd}, )

    tgt.add_task(auto.OP_FOLLOW_LINK, {'url_regex': r'xskbcx\.aspx'})
    tgt.add_task(auto.OP_SELECTFORM, 'xskb_form')
    tgt.add_task(auto.OP_CUSTOM, _automator_curriculum_helper)

# UPDATED 20110828: the mighty empty entry in year selection box is gone...
# Which meant that another true element must be chosen...
def req_curriculum_page(tgt, yr, term, yr_alt, term_alt, raw=False):

    # FIXED: Changed to the enhanced preprocessor interface...
    def filter_out_unneeded_cells(rowidx, colidx, utxt):
        '''\
        This is needed because the RowspanTitledTable, as its name suggests,
        cannot process colspan attribute used by the curriculum HTML, thus
        not accepting the scraped table structure.
        Simply filter out the unwanted cells once we encounter them.
        '''

        if utxt in [u'上午', u'下午', u'晚上', ]:
            return (False, None, ) # filtered=True cooked=None
        return (True, utxt, ) # filtered=False cooked=utxt

    def _get_a_table_outta_current_page(tgt_var):
        nodename = tgt_var + '_node'
        tgt.add_task(auto.OP_STORE_NODE, nodename)
        # reuse the content node...
        tgt.add_task(auto.OP_CSSSELECT, nodename, '#Table1', nodename)
        tgt.add_task(auto.OP_CHOOSEONE, nodename, 0, nodename)
        tgt.add_task(auto.OP_PARSEROWSPANTABLE, nodename, tgt_var,
                     filter_out_unneeded_cells) # filter_fn

    # maybe some kind of kludge is needed
    # workaround the nasty empty table problem when directly altering

    tgt.add_task(auto.OP_SELECTFORM, 'xskb_form')
    tgt.add_task(auto.OP_FILLFORM, {'xnd': [yr_alt]})
    tgt.add_task(auto.OP_EVENTTARGET, 'xnd')
    tgt.add_task(auto.OP_SUBMIT)

    tgt.add_task(auto.OP_SELECTFORM, 'xskb_form')
    tgt.add_task(auto.OP_FILLFORM, {'xnd': [yr]})
    tgt.add_task(auto.OP_EVENTTARGET, 'xnd')
    tgt.add_task(auto.OP_SUBMIT)

    # come to term selection...
    tgt.add_task(auto.OP_SELECTFORM, 'xskb_form')
    tgt.add_task(auto.OP_FILLFORM, {'xqd': [term_alt]})
    tgt.add_task(auto.OP_EVENTTARGET, 'xqd')
    tgt.add_task(auto.OP_SUBMIT)
    if raw:
        tgt.add_task(auto.OP_STORE_CONTENT, 'alt_c_tbl', enc=PAGE_ENCODING)
    else:
        _get_a_table_outta_current_page('alt_c_tbl')

    # finally get it back
    tgt.add_task(auto.OP_SELECTFORM, 'xskb_form')
    tgt.add_task(auto.OP_FILLFORM, {'xqd': [term]})
    tgt.add_task(auto.OP_EVENTTARGET, 'xqd')
    tgt.add_task(auto.OP_SUBMIT)
    if raw:
        tgt.add_task(auto.OP_STORE_CONTENT, 'c_tbl', enc=PAGE_ENCODING)
    else:
        _get_a_table_outta_current_page('c_tbl')

def req_prepare_scores(tgt):
    # a large part of this code is likely to be discarded
    tgt.add_task(auto.OP_FOLLOW_LINK, {'url_regex': r'xscjcx\.aspx'})
    tgt.add_task(auto.OP_STORE_NODE, 'score_pg', False)
    tgt.add_task(auto.OP_CSSSELECT, 'score_pg', '#ddlXN', 'yr_opts')
    tgt.add_task(auto.OP_CSSSELECT, 'score_pg', '#ddlXQ', 'term_opts')
    tgt.add_task(auto.OP_CSSSELECT, 'score_pg', '#ddl_kcxz', 'kind_opts')
    tgt.add_task(auto.OP_CHOOSEONE, 'yr_opts', 0, 'yr_opts')
    tgt.add_task(auto.OP_CHOOSEONE, 'term_opts', 0, 'term_opts')
    tgt.add_task(auto.OP_CHOOSEONE, 'kind_opts', 0, 'kind_opts')

def req_scores(tgt):
    tgt.add_task(auto.OP_SELECTFORM, 'Form1')
    tgt.add_task(auto.OP_SUBMIT, {'id': 'btn_zcj'})
    tgt.add_task(auto.OP_STORE_NODE, 'allscores_pg')
    tgt.add_task(auto.OP_CSSSELECT, 'allscores_pg', '#Datagrid1', 'score_tbl')
    tgt.add_task(auto.OP_CHOOSEONE, 'score_tbl', 0, 'score_tbl')
    tgt.add_task(auto.OP_PARSETABLE, 'score_tbl', 'scores')

################################################################
## UNDERLYING RE OPERATIONS
################################################################

def parse_basicinfo_str(u):
    match = _BASIC_INFO_RE.match(u)
    if match is not None:
        return (match.group(u'studno'), match.group(u'name'))
    else:
        raise ValueError('invalid basic info string format')

################################################################
## AUTO-REMINDER BACKEND
################################################################

def parse_curriculum(tbl):
    '''\
    Takes a ``RowSpanTitledTable`` containing the processed curriculum table,
    and formulate it.
    '''
    result = [[] for i in range(7)]

    # Use cooked data.
    # Drop the first row which is an empty line indicating "Morning".
    for row_idx, row in enumerate(tbl.processed[1:]):
        # this table's weekdays start from Monday, which is coincidentally the
        # same as Python's datetime.datetime, so processing is easy here~
        # still one point worth noting: the first cell in a row is a time tag,
        # so we have to drop it first using a simple slice operation.
        for weekday, (txt, dur) in row[1:]:
            if len(txt) != 0:
                result[weekday - 1].append(parse_period_info(txt,
                        row_idx + 1, dur))
    return result

def parse_period_info(u, start, duration):
    '''\
    Takes a Unicode string as processed by ``parse_rowspantable_into_list``
    in ``gingerprawn.api.webop.htmlparse``, and break down the string into
    several useful parts.

    In case of an omitted ``duration`` group, the pos. of period shall also
    be passed into this function, so that correct values can be determined w/o
    relying on the string itself.

    Returns a ``dict`` containing processed info about that period,
    raising ``ValueError`` if the string is not recognizable.

    The RE used is (ur'(?P<coursename>.*)\n'
                    ur'(?P<coursetype>.*)\n'
                    ur'(?:周.第(?P<duration>\d+(?:,\d+)*)节)*'
                    ur'\{第(?P<weekspan>\d+-\d+)周(?:\|(?P<weekprop>.*))*\}\n'
                    ur'(?P<teacher>.*)\n'
                    ur'(?P<location>.*)'
                    ) now.

    XXX In case the RE is updated, be sure to update both the definition and
    this docstring.
    '''
    # print u'原字符串：%s' % u.replace(u'\n', ur'\n'), # DEBUG
    matches = [i for i in _PERIOD_INFO_RE.finditer(u)]
    if not matches:
        raise ValueError('unrecognizable period info string')
    # print u'解析通过'

    # deal w/ the possible multiple descriptions...
    # you see that w/ Python this expansion is VERY easy!
    # But this comes at the cost of a change in data structure from the former
    # straightforward dict to a nested monster-like dict...
    weeks = {}
    for match in matches:
        grp = match.group
        coursename = grp(u'coursename')
        # coursetype = grp(u'coursetype') -- this is not currently important
        dur = grp(u'duration') # WARNING: This can be None!
        weekspanstr = grp(u'weekspan')
        weekprop = grp(u'weekprop') # WARNING: This can be None!
        # postprocess a little to remove spaces
        teacher = grp(u'teacher').replace(u' ', u'')
        location = grp('location')

        if dur is not None:
            # duration must be contiguous, so only the first and the last is
            # meaningful
            tmp = dur.split(u',')
            dur = (int(tmp[0]), int(tmp[-1]))
            # consistency check considered not necessary... since the jwxt
            # web backend always feeds us the right data.
            # Also this check is bound to fail if it faces more than one
            # descriptions SHARING THE SAME TABLE CELL. The field that changes
            # among these desc's is just duration.
        else:
            # accurate duration not given in the string, must use sensible
            # defaults based on the position of the corresponding cell in the
            # table.
            dur = (start, start + duration - 1)

        weekspan = [int(i) for i in weekspanstr.split(u'-')]
        tmp_weeks = range(weekspan[0], weekspan[1] + 1)

        # TODO: parse weekprop even harder
        # This parsing of weekprop can only reside here, not in another func,
        # because other variables may get modified (such as weeks), and it'd
        # be nasty if we explicitly pass ALL of them around.
        if weekprop is None:
            weekprop = u''
        else:
            if u'单周' in weekprop:
                # every odd week
                tmp_weeks = [i for i in tmp_weeks if i % 2 == 1]
                # mark as 'processed'
                weekprop = weekprop.replace(u'单周', u'')
            elif u'双周' in weekprop:
                # every even week
                tmp_weeks = [i for i in tmp_weeks if i % 2 == 0]
                weekprop = weekprop.replace(u'双周', u'')

        # Unlike weekprop, parsing location str is pretty straightforward, only
        # having to drop some extra info when the building is the 1st or 2nd
        # Teaching Building.
        location = parse_location(location)

        # build a dict mapping week ordinals to the respective classroom, etc.
        # info, being very easy to look up while maintaining flexibility.
        # We have no dict comprehension in Python 2.6..... sigh
        tmp_dct = dict(zip(tmp_weeks,
                # fill in the same info for each week
                ({'duration': dur,
                  'location': location,
                  'weekprop': weekprop,
                 } for i in tmp_weeks)))
        # merge into result
        weeks.update(tmp_dct)

    result = {'name': coursename,
              'teacher': teacher,
              'weeks': weeks,
              }
    return result

def parse_location(u):
    '''\
    Takes a Unicode string representing the classroom location, and process
    (often simplifying) it as needed.
    '''
#    if u[:2] in [u'一教', u'二教', ]:
#        # the 1st or 2nd Teaching Building, so the string is of the format
#        # ur'[一二]教[12][ABCD]\d\d\d[普多外]', the last part indicating
#        # property of the classroom, meaning almost nothing to students.
#        # Throw away prefix and suffix, leaving only the middle part
#        # (which is exactly what we need to locate the classroom.)
#        u = u[2:-1]
    # CORRECTED: the above idea produces incorrect results when it comes to
    # those classrooms managed by the School of Foreign Languages.
    # Changed to using an RE instead.
    if u[:2] in [u'1教', u'2教', ]:
        l = _LOCATION_SIMPLIFIER_RE.findall(u)
        if l:
            return l[0]
        # Simplification failed. Fall back to the good old plain string.
    return u

# this is only test-purpose, archived here to serve as a good debugging aid
# when it comes to the curriculum auto-reminder data structure.
def _test_show(st):
    for weekday, lst in enumerate(st):
        print u'星期%s' % u'一二三四五六日'[weekday]
        for course in lst:
            print u'课程：%s\n教师：%s' % (course['name'],course['teacher'],)
            for weekord, dat in sorted(course['weeks'].items()):
                print u'  第%d周: 教室 %s，第 %d 到第 %d 节课，周属性`%s\'' % (
                        weekord,
                        dat['location'],
                        dat['duration'][0],
                        dat['duration'][1],
                        dat['weekprop'],
                        )
            print


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
