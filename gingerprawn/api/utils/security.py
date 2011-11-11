#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.utils / security routines collection
# the functions for mangling secret content in situations where clear text is
# definitely necessary, are taken from my paused Lojban online dict project,
# pyjvs.
#
# Copyright (C) 2010-2011 Wang Xuerui <idontknw.wang@gmail.com>
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

# for all sorts of sanity check
import re as _re

from random import choice as _choice
from random import seed as _seed
import base64 as _base64

MODULENAME_PAT = r'^[A-Za-z_][0-9A-Za-z_]*$'
MODULENAME_VERIFIER = _re.compile(MODULENAME_PAT)

def is_valid_modulename(modname):
    return MODULENAME_VERIFIER.match(modname) is not None

def obfuscate(s):
    '''\
    Simple Obfuscation Utility
    Output: URURURURUR...UR where
    U stands for chars in the clear text, and
    R stands for chars randomly generated.
    '''
    length = len(s)
    _seed()
    randrange = [chr(i) for i in range(0x20, 0x7f)]
    # Randomized chars
    tmp2 = [_choice(randrange) for i in range(length)]
    # Interpolate
    # This integer division is Python 2.x-specific, but since
    # Django hasn't supported Py3k yet, this shouldn't cause
    # problem in understanding
    return ''.join(s[i/2] if i%2==0 \
              else tmp2[i/2] \
                   for i in range(length*2))

def obfuscate_b64(s):
    return _base64.urlsafe_b64encode(obfuscate(s))

# hehe so simple the "protection" is
def clarify(s):
    # make full use of new powerful syntax
    return s[::2]

def clarify_b64(s):
    if issubclass(type(s), unicode):
        s=s.encode('utf-8')
    s_interpolated = _base64.urlsafe_b64decode(s)
    if not s_interpolated:
        # return empty instead of complaining
        return ''
    if len(s_interpolated) % 2 != 0:
        raise TypeError('Bad request!')
    return clarify(s_interpolated)

_ob64_PADDINGTABLE = {
                      0: '',
                      1: '===',
                      2: '==',
                      3: '=',
                      }

def obfuscate_ob64(s):
    b64 = obfuscate_b64(s).strip('=')
    extra = len(b64) % 4
    return ''.join([b64[::-1], _ob64_PADDINGTABLE[extra], ])

def clarify_ob64(s):
    b64 = s.strip('=')
    extra = len(b64) % 4
    return clarify_b64(''.join([b64[::-1], _ob64_PADDINGTABLE[extra], ]))


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
