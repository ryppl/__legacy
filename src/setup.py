#!/usr/bin/env python
# -*- encoding: utf8 -*-
__revision__ = "$Id$"
import sys
import os

from distutils2.core import setup
from distutils2.command.sdist import sdist
from distutils2.command.install import install
from distutils2 import __version__

f = open('README.txt')
try:
    README = f.read()
finally:
    f.close()

def get_tip_revision(path=os.getcwd()):
    try:
        from mercurial.hg import repository
        from mercurial.ui import ui
        from mercurial import node
        from mercurial.error import RepoError
    except ImportError:
        return 0
    try:
        repo = repository(ui(), path)
        tip = repo.changelog.tip()
        return repo.changelog.rev(tip)
    except RepoError:
        return 0

DEV_SUFFIX = '.dev%d' % get_tip_revision('..')

class install_hg(install):

    user_options = install.user_options + [
            ('dev', None, "Add a dev marker")
            ]

    def initialize_options(self):
        install.initialize_options(self)
        self.dev = 0

    def run(self):
        if self.dev:
            self.distribution.metadata.version += DEV_SUFFIX
        install.run(self)


class sdist_hg(sdist):

    user_options = sdist.user_options + [
            ('dev', None, "Add a dev marker")
            ]

    def initialize_options(self):
        sdist.initialize_options(self)
        self.dev = 0

    def run(self):
        if self.dev:
            self.distribution.metadata.version += DEV_SUFFIX
        sdist.run(self)

setup_kwargs = {}
if sys.version < '2.6':
    kwargs['scripts'] = 'distutils2/mkpkg.py'

setup (name="Distutils2",
       version=VERSION,
       description="Python Distribution Utilities",
       author="Tarek Ziade",
       author_email="tarek@ziade.org",
       url="http://www.python.org/sigs/distutils-sig",
       license="PSF",
       long_description=README,
       packages=['distutils2',
                 'distutils2.command',
                 'distutils2.tests',
                 'distutils2._backport'],
       cmdclass={'sdist': sdist_hg, 'install': install_hg},
       **setup_kwargs
       )


