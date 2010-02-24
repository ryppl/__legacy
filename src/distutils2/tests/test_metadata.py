"""Tests for distutils.command.bdist."""
import unittest2
import os
import sys

from distutils2.metadata import DistributionMetadata, _interpret

class DistributionMetadataTestCase(unittest2.TestCase):


    def test_interpret(self):
        platform = sys.platform
        version = sys.version.split()[0]
        assert _interpret("sys.platform == '%s'" % platform)
        assert _interpret("sys.platform == '%s' or python_version == '2.4'" \
                % platform)
        assert _interpret("sys.platform == '%s' and "
                          "python_full_version == '%s'"\
                % (platform, version))
        assert _interpret("'%s' == sys.platform" % platform)

        # need to test errors, and " and various forms
        # and add other operators

def test_suite():
    return unittest2.makeSuite(DistributionMetadataTestCase)

if __name__ == '__main__':
    run_unittest(test_suite())
