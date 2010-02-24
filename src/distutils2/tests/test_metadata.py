"""Tests for distutils.command.bdist."""
import unittest2
import os
import sys

from distutils2.metadata import DistributionMetadata, _interpret

class DistributionMetadataTestCase(unittest2.TestCase):


    def test_interpret(self):
        platform = sys.platform
        assert _interpret("sys.platform == '%s'" % platform)


def test_suite():
    return unittest2.makeSuite(DistributionMetadataTestCase)

if __name__ == '__main__':
    run_unittest(test_suite())
