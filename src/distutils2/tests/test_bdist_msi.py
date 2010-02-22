"""Tests for distutils.command.bdist_msi."""
import unittest2
import sys

from test.test_support import run_unittest

from distutils2.tests import support

@unittest2.skipUnless(sys.platform=="win32", "These tests are only for win32")
class BDistMSITestCase(support.TempdirManager,
                       support.LoggingSilencer,
                       unittest2.TestCase):

    def test_minial(self):
        # minimal test XXX need more tests
        from distutils2.command.bdist_msi import bdist_msi
        pkg_pth, dist = self.create_dist()
        cmd = bdist_msi(dist)
        cmd.ensure_finalized()

def test_suite():
    return unittest2.makeSuite(BDistMSITestCase)

if __name__ == '__main__':
    run_unittest(test_suite())
