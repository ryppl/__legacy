"""Tests for distutils.extension."""
import unittest2
import os
import warnings

from test.test_support import check_warnings
from distutils2.extension import Extension
from distutils2.tests.support import capture_warnings

class ExtensionTestCase(unittest2.TestCase):

    pass

def test_suite():
    return unittest2.makeSuite(ExtensionTestCase)

if __name__ == "__main__":
    unittest2.main(defaultTest="test_suite")
