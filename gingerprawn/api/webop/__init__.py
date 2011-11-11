#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.webop / Automated HTTP sessions -- init section
# XXX This code seems to be UNUSED... consider elimination
#
# Copyright (C) 2011 Chen Huayue <489412949@qq.com>
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

import sys
import time

import urllib
import urllib2

from gingerprawn.api import logger
logger.install()

header=[]

# opener placeholder
OPENER = None

def init():
    global OPENER
    OPENER = urllib2.build_opener(urllib2.HTTPHandler)
    urllib2.install_opener(OPENER)
    logdebug('web operation module initialized')

def append_header(*args, **kwargs):
    header.append(*args, **kwargs)

def get_url(BaseURL):
    '''\
    Should be used only if content doesn't matter.
    '''

    try:
        f=urllib2.urlopen(BaseURL)
        _url=f.geturl()
        f.close()
        return _url
    except urllib2.HTTPError:
        logexception('Error opening URL %s', _url)
        # let the caller clean up the ground
        raise

def fetch_page(url):
    try:
        t=urllib2.urlopen(url)
        if t is not None:
            result = t.read()
        else:
            result = None
    except urllib2.HTTPError:
        logexception('Failed to fetch URL %s', url)
        # sys.exit()
    finally:
        t.close()

    return result

def post_data(url, data):
    d = urllib.urlencode(data)
    req = urllib2.Request(url,d)
    t = urllib2.urlopen(req)
    if t:
        return t.read()
    else:
        return None

def ParseURL(url):
    # TODO: do this in more Pythonic way.
    u='/'.join(url.split('/')[:-1])
    u+='/'
    return u

def ParseHTML(content):
    tmp=re.sub('<br>','\n',content)
    tmp=re.sub('&nbsp;',' ',tmp)
    tmp=re.sub('<.*?>','',tmp)
    tmp=re.sub('\t','',tmp)
    return tmp


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
