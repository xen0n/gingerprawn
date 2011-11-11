#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gingerprawn / api.conf / customized ver. of SafeConfigParser
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

__all__ = ['GingerprawnConfig',
           ]

from ConfigParser import SafeConfigParser
from ConfigParser import NoSectionError, DuplicateSectionError, NoOptionError

# for (naive) Python object storage
from gingerprawn.api.utils.pickler import bzb64dumps, bzb64loads

class GingerprawnConfig(SafeConfigParser):
    '''\
    This is the customized ``SafeConfigParser`` used throughout the
    gingerprawn framework.
    This class has an ``ensure_section`` method that does nothing when
    invoked w/ an already existing section name.
    Also, this class can remember the config filename, and write back to it
    automatically.
    '''

    def ensure_section(self, section):
        '''\
        Ensures that a particular section exists before trying to
        access it, so that unwanted ``NoSectionError`` won't arise.
        This is done by catching and ignoring the ``DuplicateSectionError``
        and ``ValueError`` which are thrown by
        ``SafeConfigParser.add_section``\ .
        '''
        try:
            self.add_section(section)
        except DuplicateSectionError:
            pass
        except ValueError:
            # "default" section encountered
            pass

    def __init__(self, fname):
        '''\
        Constructor. Accepts the config file path as a mandatory parameter,
        remembers that, and initializes ``self`` with that file.
        '''
        SafeConfigParser.__init__(self)
        self.__fname = fname
        # with open(fname, 'rb') as cfgfile:
        #     self.readfp(cfgfile)
        self.read([fname])

        # set status to "unmodified"
        self.__intact = True

    def writeback(self):
        '''\
        Update the original config file.
        '''
        # peek, is settings unmodified? if it is the case, do nothing
        if self.__intact:
            return
        with open(self.__fname, 'wb') as cfgfile:
            self.write(cfgfile)

    def __del__(self):
        # to maintain coherency when (accidentally) deleted w/o cleanup
        self.writeback()
        # base class doesn't have this dtor
        # ConfigParser.SafeConfigParser.__del__(self)

    def get(self, section, option,
            default=None, throw_exc=False, **kwargs):
        '''\
        Extended version of ``get``\ , supporting default fallback value and
        explicit exception handling (swallowing or re-throwing).
        '''
        try:
            return SafeConfigParser.get(self, section, option, **kwargs)
        except NoOptionError:
            if throw_exc:
                raise
            return default
        except NoSectionError:
            if throw_exc:
                raise
            return default

    ############################################################
    ## Wrappers needed to implement status-tracking
    def set(self, *args, **kwargs):
        SafeConfigParser.set(self, *args, **kwargs)
        # set status to "modified"
        self.__intact = False

    def add_section(self, *args, **kwargs):
        SafeConfigParser.add_section(self, *args, **kwargs)
        # set status to "modified"
        self.__intact = False

    def get_obj(self, section, option, default=None, throw_exc=False):
        s = self.get(section, option, None, throw_exc)

        # This is the string (cPickled) representation of the object,
        # so if this get returned None the requested option must be
        # non-existent.
        if s is None:
            # if throw_exc is True, we can't reach here
            return default
        # unpickle the serialized object
        tmp = bzb64loads(s)
        return tmp

    def set_obj(self, section, option, obj):
        tmps = bzb64dumps(obj)
        self.set(section, option, tmps)
        del tmps


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
