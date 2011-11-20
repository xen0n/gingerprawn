gingerprawn
===========

This is **gingerprawn**, a modular pluggable framework for wxPython;
and **JNMaster**, a bunch of plugins written on top of gingerprawn, intended
to help students in Jiangnan University, Wuxi, China to make better use of
the school intranet.


Runtime dependencies
--------------------

``gingerprawn.api.webop`` depends on ``lxml`` and ``mechanize``. You can get
them like this:

    $ sudo easy_install -U --always-unzip mechanize

    $ sudo easy_install -U --always-unzip lxml

or via their websites: http://lxml.de/ and http://wwwsearch.sourceforge.net/mechanize\ .

Of course, as a wxPython framework, ``gingerprawn`` requires wxPython. The
version must be *at least 2.8*, and *the Unicode version is needed*. You can
get wxPython at its official website <http://www.wxpython.org/>.


Notes on development
--------------------

For development you would want to use **eric4** as the IDE or just stick to Vim
or Emacs or whatever editor you use. An eric4 project is included in the repo.

Development is at a very early stage, and the codebase is not promised to
keep stable at the moment. If you feel like to contribute, contact the author:

    Wang Xuerui (xenon at JNRain) <idontknw dot wang at gmail-dot-com>


.. vim:ai et ts=4 sw=4 sts=4 fenc=utf-8 syntax=rst
