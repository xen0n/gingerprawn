#!/usr/bin/env python
# -*- coding: utf-8 -*-

HEADER_FORMAT = u'''\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wx.lib.embeddedimage import PyEmbeddedImage

'''.encode('utf-8-sig')

FOOTER_FORMAT = '''\

# vi:ai:et:ts=2 sw=2 sts=2 ff=unix fenc=utf-8
'''

IMAGE_ENTRY_FORMAT = '''\
# generated from file '%(fname)s'
%(ident)s = PyEmbeddedImage(
%(b64str)s)

'''

def add_quote(data):
    return ('"%s"' % l for l in data.encode('base64').split('\n')[:-1])

def gen_string(data):
    return '\n'.join(add_quote(data))

def squeeze_data(data, ident, fname):
    return IMAGE_ENTRY_FORMAT % {'ident': ident,
            'b64str': gen_string(data),
            'fname': fname,
            }

def read_data(fname):
    fp = open(fname, 'rb')
    s = fp.read()
    fp.close()
    return s

def conv(fname, ident, fp):
    content = read_data(fname)
    fp.write(squeeze_data(content, ident, fname))

def main(argv):
    del argv[0]
    outname = argv[-1]
    del argv[-1]

    count = 0
    fp = open(outname, 'wb')
    fp.write(HEADER_FORMAT)
    
    for f in argv:
        print "converting '%s'" % f
        ident = raw_input('identifier name: ')
        try:
            conv(f, ident, fp)
            count += 1
        except IOError:
            print "I/O error happened, continuing to the next file"
            continue
        except KeyboardInterrupt:
            print "User break"
            break

    fp.write(FOOTER_FORMAT)
    fp.close()

    print 'converted %d image(s), exiting' % count

if __name__ == '__main__':
    import sys
    main(sys.argv)

# vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
