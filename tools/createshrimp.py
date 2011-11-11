#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from optparse import OptionParser

import re # for shrimp module name sanity checking

realpath = os.path.realpath
normpath = os.path.normpath
pathjoin = os.path.join
dirname = os.path.dirname

if hasattr(sys, "frozen"):
    SELF_DIR = realpath(dirname(unicode(sys.executable,
                                        sys.getfilesystemencoding())))
else:
    SELF_DIR = realpath(dirname(unicode(__file__, sys.getfilesystemencoding())))

TEMPLATE_PATH = pathjoin(SELF_DIR, '_shrimp_template.py.txt')
NAME_VERIFIER = re.compile(r'^[A-Za-z_][0-9A-Za-z_]*$')

USAGE = 'usage: %prog [options] shrimp_name [shrimp_name ...]'
parser = OptionParser(usage=USAGE)
o = parser.add_option
o('-a', '--author', dest='author', default='gingerprawn team',
        help='set author name to AUTHOR', metavar='AUTHOR')
o('-q', '--quiet', dest='verbose', action='store_false', default=True,
        help='print less messages to stdout')
del o

def main():
    options, args = parser.parse_args()

    if len(args) == 0:
        parser.error('there must be at least one shrimp to create')

    for name in args:
        if NAME_VERIFIER.match(name) is None:
            parser.error("'%s' is not a valid shrimp name" % name)

    shrimp_list = [name.lower().decode('ascii') for name in args]
    author = unicode(options.author,
            'gbk' if sys.platform == 'win32' else 'utf-8')
    verbose = options.verbose

    if verbose:
        print 'creating shrimp', ', '.join(shrimp_list)
        print 'the author is', author
        print '\nloading template...',
    try:
        template = open(TEMPLATE_PATH).read()
    except IOError:
        print >>sys.stderr, 'ERROR: template loading failed'
        sys.exit(1)
    if verbose:
        print 'ok'

    template = unicode(template, 'utf-8-sig')

    for sh in shrimp_list:
        if verbose:
            print 'creating shrimp', sh
        # lowername is sh itself
        shrimp_content = template % {'lowername': sh,
                'uppername': sh.upper(),
                'capname': sh.capitalize(),
                'author': author,
                }
        shrimp_filename = '%s_main.py' % sh
        if verbose:
            print 'writing %s...' % shrimp_filename,
        try:
            os.mkdir(sh)
            fp = open(pathjoin(sh, shrimp_filename), 'wb')
            fp.write(shrimp_content.encode('utf-8'))
        except IOError:
            print >>sys.stderr, 'ERROR: writing to file "%s" failed' \
                    % shrimp_filename
            continue
        finally:
            fp.close()
        if verbose:
            print 'ok'
    print 'all done'
    sys.exit(0)

if __name__ == '__main__':
    main()

# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
