#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Boa:App:GingerPrawn
# gingerprawn / launcher / entry point; loader driver
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

import sys

# FIX ENCODING!!
# FIXME: use anything sensible to replace this line as soon as
# I come up with an appropriate idea
reload(sys)
# Use fs encoding.
sys.setdefaultencoding(sys.getfilesystemencoding())

import os

import __builtin__
_tgt = __builtin__.__dict__

# for parsing of command line options
from optparse import OptionParser

# our module path determiner
import modpath

normpath = os.path.normpath
pathjoin = os.path.join

#################################################
## freeze status detection made earlier

if not modpath.we_are_frozen():
    # HAH! Logging facility is not ready yet!
    # logdebug('Running in true Python env')
    _IS_FROZEN = _tgt['_IS_FROZEN'] = False
else:
    # logdebug('Running in frozen py2exe env')
    _IS_FROZEN = _tgt['_IS_FROZEN'] = True

################################################################
## remember our executable file name, mainly for the purpose of
## auto-starting.
## MODIFIED: Path preparation made as early as possible
try:
    # Store the application executable's path in the builtin namespace.
    _apppath = _NOCONSOLE_FILE
except NameError:
    # not running in console-less mode, revert to main.py's path
    if _IS_FROZEN:
        # __file__ doesn't exist, pass a dummy value
        _apppath = None
    else:
        _apppath = __file__ # normal manner...

_tgt['_APP_EXECUTABLE'] = modpath.executable_path(_apppath)

# path determination now use py2exe-compatible way
# mypath is .../gingerprawn/launcher, # renamed just before going for a DVCS
# toplev is mypath's parent dir
mypath = modpath.module_path(_apppath)
toplev = normpath(pathjoin(mypath,'..'))

if __name__ == '__main__' or _tgt.has_key('_NOCONSOLE_FILE'):
    # running as a real app
    # make gingerprawn module available
    sys.path.insert(0, normpath(pathjoin(toplev, '..')))
    # go to pkg toplevel for easy maintenance
    os.chdir(toplev)

# I've had enough with the endless passing of toplev
# So give it only one place to reside...
_tgt['_PKG_TOPLEV'] = toplev

#################################################
# initialize option parser
# DONE: verbosity level supported via logger
parser = OptionParser()
o = parser.add_option

o('-m', '--module', dest='mainmod', metavar='SHRIMP', default='lobster',
        help='override default main module with SHRIMP')
o('-A', '--autostart', dest='autostart', action='store_true', default=False,
        help='indicate we are launched alongside OS start; don\'t use this')
o('-p', '--profile', dest='do_profiling', action='store_true', default=False,
        help='Profile the running for optimization purposes')
o('-s', '--shell', dest='run_shell', action='store_true', default=False,
        help='run interactive debug shell')
o('--psyco', dest='run_psycoed', action='store_true', default=False,
        help='run w/ Psyco acceleration if available')
o('-U', '--univ', dest='univ_sel', metavar='UNIV', default='jiangnan',
        help='use university UNIV\'s support library')

if not _IS_FROZEN:
    o('-Z', '--zip', dest='zipped_shrimp', action='store_true', default=False,
            help='only recognize zipped shrimp (only in dev version)')
else:
    o('-r', '--raw', dest='zipped_shrimp', action='store_false', default=True,
            help='recognize shrimp source code (only in EXE dists)')
del o

# global holder to move option parsing earlier to enhance cmdline experience
(options, args, ) = parser.parse_args()
# announce parameters as early as possible
_tgt['_APP_OPTIONS'] = options
_tgt['_APP_ARGS'] = args

################################################################
## Real initialization starts here, after all options are in
## their places.

# first the conf manager
from gingerprawn.api import conf

# init logging infrastructure
from gingerprawn.api import logger
logger.init()
logger.install()

# init the launcher itself
# XXX this is not needed... currently there is no work to be done here
# import gingerprawn.launcher

if _IS_FROZEN:
    logdebug('running frozen')
else:
    logdebug('running free')

if logisdebug():
    logdebug('Options: %s; Remaining args: %s', repr(options), repr(args))

################################################################
## IMPORT WXPYTHON PACKAGE

if not _IS_FROZEN:
    # not in frozen environment, select a best version for use
    import wxversion
    wxversion.select('2.8.11-unicode')

import wx
logdebug('wx version %s', wx.version())

from gingerprawn.api.cooker import iconmgr

import LobsterLoader

# this var is only useful for Boa
# trimmed most entries out
modules ={
 'LobsterLoader': [1, u'Splashscreen and loader of gingerprawn',
                   u'./LobsterLoader.py'],
}

class GingerPrawn(wx.App):
    def OnInit(self):
        # delayed invocation of gdi routines
        iconmgr.init()

        # custom code added to pass information to loader
        # modified parameter passing mechanism in order to inform the loader
        # of whether we are starting along with OS at an early stage enough
        # to allow modification of splash behavior.
        # that code got moved even earlier, just after options are parsed,
        # so here only remains the passing of the App object.
        _tgt['_APP_OBJECT'] = self

        # skeleton I18N mechanism init
        # We need a wx.Locale object.
        # This may get done in the 2nd release of gingerprawn
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        if self.locale.IsOk():
            loginfo('Locale set to %s (%s)', self.locale.GetLocale(),
                    self.locale.GetName())
            pass
        else:
            logwarning('Failed to set locale, falling back')
            # not sure whether this is needed
            del self.locale
            self.locale = None

        self.main = LobsterLoader.create(None)

        self.main.Show()
        self.SetTopWindow(self.main)
        return True

    def _On_LobsterInit(self, lobster_frame_creator):
        logdebug('Callback from metashrimp, let it take over control')
        self.tmpmain = lobster_frame_creator(None)
        self.tmpmain.Show()
        self.SetTopWindow(self.tmpmain)
        self.main.Destroy()
        self.main = self.tmpmain
        del self.tmpmain

    def _On_ShrimpInit(self, shrimp_frame_creator):
        # keep this distinct from LobsterInit since this doesn't need
        # killing and replacing the current main frame
        loginfo("trying to show sub-shrimp")
        tmp = shrimp_frame_creator(self.main)
        tmp.Show()
        # TODO: figure out a way to keep the frame object's reference

def wxmain():
    application = GingerPrawn(0)
    application.MainLoop()
    # NOTE: log message priority revised, an INFO is more appropriate
    # because this information is potentially useful to the end user,
    # unlike debug messages which are only meaningful to developers.
    loginfo('Application exit.')

def main():
    if options.run_shell:
        # Due to univlib init code having been moved into initthread,
        # we must duplicate (ugh!) the univlib initialization code here
        # in order to maintain easiness in shell operations
        # the code is directly copied from LobsterLoader
        # TODO: refactor this once i come up with a solution

        ### START COPY ###
        # init univlib ahead of time
        from gingerprawn.api import univlib
        # FIXED: not hardcoded anymore, can be changed via cmdline
        # default value moved there
        univlib.set_current_univ(_APP_OPTIONS.univ_sel)
        ### END OF COPY ###

        import code
        conzole = code.InteractiveConsole()
        conzole.interact()
        sys.exit(0)

    if not options.do_profiling:
        if options.run_psycoed:
            try:
                import psyco
                logdebug('running Psyco\'d')
                psyco.log()
                psyco.profile()
            except ImportError:
                pass
        wxmain()
    else:
        import cProfile
        loginfo('running profiled, starting from here...')
        cProfile.run('wxmain()',
                # profile result destination
                normpath(pathjoin(_PKG_TOPLEV, 'launcher/gp-profile')))

if __name__ == '__main__':
    main()


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
