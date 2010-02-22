#!/usr/bin/env python
# -*- encoding: utf8 -*-
__revision__ = "$Id$"
import sys
import os

from distutils2.core import setup
from distutils2.command.sdist import sdist

VERSION = '1.0a1'

f = open('README.txt')
try:
    README = f.read()
finally:
    f.close()

class sdist_hg(sdist):

    user_options = sdist.user_options + [
            ('dev', None, "Add a dev marker")
            ]

    def initialize_options(self):
        sdist.initialize_options(self)
        self.dev = 0

    def run(self):
        if self.dev:
            suffix = '.dev%d' % self.get_tip_revision()
            self.distribution.metadata.version += suffix
        sdist.run(self)

    def get_tip_revision(self, path=os.getcwd()):
        from mercurial.hg import repository
        from mercurial.ui import ui
        from mercurial import node
        repo = repository(ui(), path)
        tip = repo.changelog.tip()
        return repo.changelog.rev(tip)

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
       cmdclass={'sdist': sdist_hg}
       )


