#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.webop / automated form crawling workflow
# xenon rewrite of web operation module, incorporating lxml and mechanize.
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

# Ultimate goal is to automate all those fetching'n'processing
# process, all encapsulated in a single Automator class

import mechanize

# this is automated.URLError, which "is" (operator, got it?)
# mechanize.URLError, which in turn is urllib2.URLError...
URLError = mechanize.URLError

from gingerprawn.api.webop import htmlparse

# from gingerprawn.api.utils.metaprogramming import methodize

DEFAULT_UA = {
    ('ff', 3): 'Mozilla/5.0 (Linux x86_64; en-US) Gecko/20110323 Firefox/3.6.16',
    ('ff', 4): 'Mozilla/5.0 (Windows NT 6.1; rv:2.0) Gecko/20100101 Firefox/4.0',
    ('ie', 9): 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    ('ie', 7): 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/5.0)',
    ('op', 11): 'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.7.62 Version/11.01',
    }

UA_FALLBACK = ('ff', 3, )

OP_CUSTOM = 'custom'

OP_OPEN = 'open'
OP_CLOSE = 'close'

OP_SELECTFORM = 'selectform'
OP_FILLFORM = 'fill'
OP_FILLREADONLY = 'fillro'
OP_EVENTTARGET = 'eventtgt'
OP_SUBMIT = 'submit'
OP_FOLLOW_LINK = 'follow'
OP_MODIFY_RESPONSE = 'setdata'

OP_CSSSELECT = 'css'
OP_CHOOSEONE = 'choose'

OP_STORE_CONTENT = 'content'
OP_STORE_URL = 'url'
OP_STORE_NODE = 'node'

OP_STORE_TEXT = 'nodetxt'

OP_PARSETABLE = 'parsetbl'
OP_PARSEROWSPANTABLE = 'rowspantbl'

# the automator prototype
class Automator(object):
    '''\
    Operation Automator for B/S Architecture Systems (prototype)

    Provides easy batch-processing of page operations, including form
    filling, smart navigation, fetching and parsing of individual pages,
    and so on.
    '''

    def __init__(self, url=None, user_agent=UA_FALLBACK):
        '''\
        ctor function.
        user_agent: a tuple of format ('<browsertype>', ver)
        where <browsertype> is one of ['ie', 'ff', 'op'], each of
        which standing for the corresponding (common) browser.

        Currently, when the given tuple is not recognized, the string as
        specified by UA_FALLBACK is used, that's Firefox 3.6.16 running under
        x86_64 Linux.
        '''
        self._UA = DEFAULT_UA.get(user_agent, UA_FALLBACK)
        self._br = mechanize.Browser()
        # set initial user-agent
        self._br.addheaders[0] = ('User-agent', self._UA, )
        # our tasklist
        self._op = []

        # for some kind of productivity increase :-P
        if url is not None:
            self.add_task(OP_OPEN, url)

    def add_task(self, opstr, *args, **kwargs):
        '''\
        Add a task to the workflow.
        opstr is one of the opcode as specified by those OP_xxx definitions;
        meanings of *args and **kwargs depend on the opcode.
        More of this in the documentation.
        '''
        self._op.append((opstr, args, kwargs, ))

    def get_tasklist(self):
        '''\
        Get the internal tasklist structure.
        Use this only if you are sure what you're doing. (-:
        '''
        return self._op

    def clear_tasklist(self):
        '''\
        Clear the current pending tasklist.
        '''
        del self._op
        self._op = []

    def execute_raw(self, processor_fn):
        '''\
        Instead of executing the tasks as given by self._op,
        invoke the user-specified processor function.
        That function is provided with the mechanize.Browser object that is
        created when ctor is called.
        '''
        processor_fn(self._br)

    def execute(self):
        '''\
        Execute the tasks in the order they're added.

        After execution, self.retcodes shall contain return codes of each
        step, True standing for success;
        self.result shall contain all of the results that is to be stored.

        Note that self.retcodes is a list while self.result is a dict.
        '''
        self.__buffer = {}
        retcodes = []
        result = {}
        for op in self._op:
            try:
                _fn = getattr(self, '_execute_%s' % op[0])
            except AttributeError:
                raise AttributeError("operation `%s' not defined" % op[0])

            try:
                outcome = _fn(*op[1], **op[2])
            except:
                # sth errorneous happened, must cleanup first
                self.retcodes = retcodes
                self.result = result
                del self.__buffer
                self.clear_tasklist()
                raise # propagate

            retcodes.append(outcome[0])
            result.update(outcome[1])

        self.retcodes = retcodes
        self.result = result
        # cleanup
        del self.__buffer
        self.clear_tasklist()

    def succeeded(self):
        try:
            self.retcodes
        except AttributeError:
            return False
        # one of the BIF's(Erlangspeak...) is called all...
        return all(self.retcodes)

################################################################
    def _execute_custom(self, fn, *args):
        return fn(self._br, self.__buffer, *args)

    def _execute_open(self, url):
        self._br.open(url)
        return (True, {}, )

    def _execute_close(self):
        self._br.close()
        return (True, {}, )

    def _execute_selectform(self, form):
        self._br.select_form(form)
        return (True, {}, )

    def _execute_fill(self, form_data):
        for field, value in form_data.items():
            self._br[field] = value
        return (True, {}, )

    def _execute_fillro(self, fieldname, txt):
        self._br.form.find_control(name=fieldname).readonly = False
        self._br[fieldname] = txt
        return (True, {}, )

    def _execute_eventtgt(self, txt):
        return self._execute_fillro('__EVENTTARGET', txt)

    def _execute_submit(self, kwargs=None):
        if kwargs is None:
            self._br.submit()
        else:
            self._br.submit(**kwargs)
        return (True, {}, )

    def _execute_follow(self, params):
        self._br.follow_link(**params)
        return (True, {}, )

    def _execute_content(self, target_var, store=True, enc=None):
        data = self._br.response().get_data()
        if enc is not None:
            data = data.decode(enc)

        self.__buffer[target_var] = data
        if store:
            return (True, {target_var: data}, )
        else:
            return (True, {}, )

    def _execute_setdata(self, newdata):
        response = self._br.response()
        response.set_data(newdata)
        self._br.set_response(response)

        return (True, {}, )


    def _execute_url(self, target_var):
        url = self._br.geturl()
        self.__buffer[target_var] = url
        return (True, {target_var: url}, )

    def _execute_css(self, node, pat, tgt_var):
        self.__buffer[tgt_var] = result = self.__buffer[node].cssselect(pat)
        return (len(result) > 0, {tgt_var: result}, )

    def _execute_node(self, tgt_var, store=True):
        # here a little bit of redundancy...
        node = self.__buffer[tgt_var] = htmlparse.fromstring(
                self._br.response().get_data())
        if store:
            return (True, {tgt_var: node}, )
        else:
            return (True, {}, )

    def _execute_choose(self, src_var, idx, tgt_var):
        self.__buffer[tgt_var] = self.__buffer[src_var][idx]
        return (True, {}, )

    def _execute_nodetxt(self, src_var, tgt_var, store=True):
        txt = self.__buffer[tgt_var] = '\n'.join(
                self.__buffer[src_var].itertext())
        if store:
            return (True, {tgt_var: txt}, )
        else:
            return (True, {}, )

    def _execute_parsetbl(self, src_var, tgt_var, filter_fn=None):
        # src_var is the table node, which can be prepared by using
        # OP_CSSSELECT and OP_CHOOSEONE in concerto
        # tgt_var is the place to store the resulting TitledTable
        ttbl = self.__buffer[tgt_var] = (
                htmlparse.parse_into_table(self.__buffer[src_var],
                        filter_fn))

        return (True, {tgt_var: ttbl}, )

    def _execute_rowspantbl(self, src_var, tgt_var, filter_fn=None):
        ttbl = self.__buffer[tgt_var] = (
                htmlparse.parse_into_rowspantable(self.__buffer[src_var],
                        filter_fn))

        return (True, {tgt_var: ttbl}, )


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
