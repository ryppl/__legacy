"""Tests for distutils.command.bdist."""
import unittest2
import sys
import os
import tempfile
import shutil

from distutils2.tests import run_unittest

from distutils2.core import Distribution
from distutils2.command.bdist import bdist
from distutils2.tests import support
from distutils2.spawn import find_executable
from distutils2 import spawn
from distutils2.errors import DistutilsExecError

class BuildTestCase(support.TempdirManager,
                    unittest2.TestCase):

    def test_formats(self):

        # let's create a command and make sure
        # we can fix the format
        pkg_pth, dist = self.create_dist()
        cmd = bdist(dist)
        cmd.formats = ['msi']
        cmd.ensure_finalized()
        self.assertEquals(cmd.formats, ['msi'])

        # what format bdist offers ?
        # XXX an explicit list in bdist is
        # not the best way to  bdist_* commands
        # we should add a registry
        formats = ['rpm', 'zip', 'gztar', 'bztar', 'ztar',
                   'tar', 'wininst', 'msi']
        formats.sort()
        founded = cmd.format_command.keys()
        founded.sort()
        self.assertEquals(founded, formats)

def test_suite():
    return unittest2.makeSuite(BuildTestCase)

if __name__ == '__main__':
    run_unittest(test_suite())
