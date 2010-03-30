#!/usr/bin/env python
__revision__ = "$Id$"
import sys
import os

from distutils.core import setup
from distutils.command.sdist import sdist
from distutils.command.install import install
from ryppl import __version__ as VERSION

f = open('README.txt')
try:
    README = f.read()
finally:
    f.close()

# TODO: translate these hg things into git?
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

class install_hg(install):

    DEV_SUFFIX = '.dev%d' % get_tip_revision('..')

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

    DEV_SUFFIX = '.dev%d' % get_tip_revision('..')

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

setup (name="Ryppl",
       version=VERSION,
       description="A Git-based Software Development / Testing / Installation System",
       author="Dave Abrahams & co.",
       author_email="dave@boostpro.com",
       url="http://ryppl.org",
       license="Boost Software License 1.0",
       long_description=README,
       packages=['ryppl',
                 'ryppl.command',
                 'ryppl.tests'],
       cmdclass={'sdist': sdist_hg, 'install': install_hg},
       **setup_kwargs
       )


