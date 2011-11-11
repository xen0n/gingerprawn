#!/usr/bin/env python
# -*- coding: utf-8 -*-
# help to examine the result of profiling

import sys
import pstats

def main(argv):
    if len(argv) != 2:
        print >>sys.stderr, u'usage: %s path/to/cprofile_file' % argv[0]
        return 2

    p = pstats.Stats(argv[1])
    p.strip_dirs().sort_stats('cumulative').print_stats()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))


# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
