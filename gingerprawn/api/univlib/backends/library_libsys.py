#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.univlib.backends / Library system ops -- for Libsys systems
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

# for generation of datestamp used by renewal routine
from time import time

from gingerprawn.api.webop import automated as auto

from gingerprawn.api import logger
logger.install()

from .library_base import LibraryBase


LOGINTYPE_CERTNO = 'cert_no'
LOGINTYPE_BARNO = 'bar_no'
LOGINTYPE_EMAIL = 'email'

################################################################
# INTERFACE CLASS

class LibsysLibrary(LibraryBase):
    def set_user_info(self, uid, psw, typ=LOGINTYPE_CERTNO):
        self._uid = uid
        self._psw = psw
        self._typ = typ

    def do_login(self):
        req_login(self._bot, self._uid, self._psw, self._typ)
        self._bot.execute()
        return self._bot.succeeded()

    def get_book_list(self):
        self.chk_last_op()

        req_booklist(self._bot)
        self._bot.execute()
        if self._bot.succeeded():
            return self._bot.result['book_tbl']
        return None

################################################################
## IMPLEMENTATION OF AUTOMATOR'S MOVES
################################################################

def req_login(tgt, username, psw, logintype=LOGINTYPE_CERTNO):
    tgt.add_task(auto.OP_SELECTFORM, 'frm_login')
    tgt.add_task(auto.OP_FILLFORM,
                 {'select': [logintype],
                  'number': username,
                  'passwd': psw,
                  })
    tgt.add_task(auto.OP_SUBMIT)

def req_booklist(tgt):
    tgt.add_task(auto.OP_FOLLOW_LINK, {'url': 'book_lst.php'})
    # TODO: deal with a potential timeout here
    tgt.add_task(auto.OP_STORE_NODE, 'lst_pg')
    tgt.add_task(auto.OP_CSSSELECT, 'lst_pg',
            'div.panel table.sortable', 'book_lst')
    tgt.add_task(auto.OP_CHOOSEONE, 'book_lst', 0, 'book_lst')
    tgt.add_task(auto.OP_PARSETABLE, 'book_lst', 'book_tbl')

def req_renew_one(tgt, barcode):
    def _do_renew(br, buf):
        # make a new button to point to what we want, in this case
        # the renewal URL.
        # Directly using AJAX may be a better option... but don't
        # know how to utilize it
        pass
    tgt.add_task(auto.OP_FOLLOW_LINK, {'url': 'book_lst.php'})

    # The idea behind this is that in order to automate submitting,
    # we have to modify all the "Renew" buttons,
    # getting rid of the JavaScript call and filling appropriate
    # POST URLs (simulating the effect of clicking), and to parse
    # the HTML returned.
    tgt.add_task(auto.OP_CUSTOM)

################################################################
## HELPER FUNCTIONS
################################################################

def jstime():
    '''\
    Simulate the JavaScript statement ``new Date().getTime()``
    '''
    return int(time() * 1000)

def gen_renew_url(url_base, barcode):
    return url_base % {'barcode': barcode, 'timestamp': jstime()}


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
